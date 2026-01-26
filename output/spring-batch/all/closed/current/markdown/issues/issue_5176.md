# ClosedChannelException and FileChannel leak when switching resources multiple times within the same transaction

**Issue番号**: #5176

**状態**: closed | **作成者**: banseok1216 | **作成日**: 2025-12-20

**ラベル**: status: duplicate

**URL**: https://github.com/spring-projects/spring-batch/issues/5176

## 内容

## Bug description

When `StaxEventItemWriter` is used **within the same transaction (TransactionTemplate)** in the following pattern, problems occur:

- Using the same `StaxEventItemWriter` instance
- `setResource(r1) -> open -> write -> close`
- `setResource(r2) -> open -> write -> close`
- `setResource(r3) -> open -> write -> close`

Observed problems (depending on the environment, one or both may occur):

1) `java.nio.channels.ClosedChannelException` at transaction commit (or at the end of transaction synchronization)  
2) Some `FileChannel`s opened for r1/r2/r3 remain open after the transaction ends (resource leak)

Related issue:
- https://github.com/spring-projects/spring-batch/issues/5098

## Environment

- Spring Batch version: 6.0.x, 5.2.x

## Steps to reproduce

1. Add the following two tests to Spring Batch codebase in `org.springframework.batch.infrastructure.item.xml.TransactionalStaxEventItemWriterTests`.
2. Run tests. You will observe either:
   - `ClosedChannelException` in `shouldWriteThreeSeparateFilesWhenMultipleOpenCloseAndResourceSwitchInSingleTransaction`, or
   - a failure in `shouldCloseAllFileChannelsAfterTransaction` because some channels remain `isOpen() == true` after transaction completion.

## Expected behavior

Even when switching resources and opening/closing the writer multiple times within the same transaction:

1) No `ClosedChannelException` should be thrown at transaction completion.  
2) After the transaction ends (commit/rollback), **all FileChannels opened during that transaction must be closed**.

## Minimal Complete Reproducible example

The following tests validate two aspects:

1) Exception reproduction: `shouldWriteThreeSeparateFilesWhenMultipleOpenCloseAndResourceSwitchInSingleTransaction`  
2) Leak reproduction: `shouldCloseAllFileChannelsAfterTransaction`  
   - It uses reflection to extract the underlying `FileChannel` and checks `isOpen()` after the transaction.

```java
@Test
void shouldWriteThreeSeparateFilesWhenMultipleOpenCloseAndResourceSwitchInSingleTransaction() throws Exception {
    WritableResource r1 = new FileSystemResource(File.createTempFile("stax-tx-rot-1", ".xml"));
    WritableResource r2 = new FileSystemResource(File.createTempFile("stax-tx-rot-2", ".xml"));
    WritableResource r3 = new FileSystemResource(File.createTempFile("stax-tx-rot-3", ".xml"));

    assertDoesNotThrow(() ->
        new TransactionTemplate(transactionManager).execute((TransactionCallback<Void>) status -> {
            try {
                writer.setResource(r1);
                writer.open(new ExecutionContext());
                writer.write(items);
                writer.close();

                writer.setResource(r2);
                writer.open(new ExecutionContext());
                writer.write(items);
                writer.close();

                writer.setResource(r3);
                writer.open(new ExecutionContext());
                writer.write(items);
                writer.close();

                return null;
            }
            catch (Exception e) {
                throw new RuntimeException(e);
            }
        })
    );
}

@Test
void shouldCloseAllFileChannelsAfterTransaction() throws Exception {
    WritableResource r1 = new FileSystemResource(File.createTempFile("stax-tx-leak-1", ".xml"));
    WritableResource r2 = new FileSystemResource(File.createTempFile("stax-tx-leak-2", ".xml"));
    WritableResource r3 = new FileSystemResource(File.createTempFile("stax-tx-leak-3", ".xml"));

    List<FileChannel> opened = new ArrayList<>();

    try {
        new TransactionTemplate(transactionManager).execute((TransactionCallback<Void>) status -> {
            try {
                writer.setResource(r1);
                writer.open(new ExecutionContext());
                FileChannel ch1 = extractChannelFromStaxWriter(writer);
                assertNotNull(ch1);
                opened.add(ch1);
                writer.write(items);
                writer.close();

                writer.setResource(r2);
                writer.open(new ExecutionContext());
                FileChannel ch2 = extractChannelFromStaxWriter(writer);
                assertNotNull(ch2);
                opened.add(ch2);
                writer.write(items);
                writer.close();

                writer.setResource(r3);
                writer.open(new ExecutionContext());
                FileChannel ch3 = extractChannelFromStaxWriter(writer);
                assertNotNull(ch3);
                opened.add(ch3);
                writer.write(items);
                writer.close();

                return null;
            }
            catch (Exception ignored) {
            }
        });
    }
    catch (Exception ignored) {
        // Continue to check leaks even if an exception happens
    }

    assertEquals(3, opened.size(), "Expected 3 opened channels");
    for (FileChannel ch : opened) {
        assertFalse(ch.isOpen(), "FileChannel should be closed after transaction");
    }
}

private static FileChannel extractChannelFromStaxWriter(StaxEventItemWriter<?> w) throws Exception {
    // legacy version
    Field field = StaxEventItemWriter.class.getDeclaredField("channel");
    field.setAccessible(true);
    return (FileChannel) field.get(w);
    
    // enhance version
    Spring Batch 6.x layout: StaxEventItemWriter.state.channel
    Field stateField = StaxEventItemWriter.class.getDeclaredField("state");
    stateField.setAccessible(true);
    Object state = stateField.get(w);
    Field channelField = state.getClass().getDeclaredField("channel");
    channelField.setAccessible(true);
    return (FileChannel) channelField.get(state);
}
```

## Observed stacktrace example

```text
org.springframework.batch.infrastructure.support.transaction.FlushFailedException: Could not write to output buffer
Caused by: java.nio.channels.ClosedChannelException
```

## Why this happens

The key is that `TransactionAwareBufferedWriter` performs **flush/close at transaction synchronization time**.

Problematic structure:

- It registers a close callback like `TransactionAwareBufferedWriter(fileChannel, this::closeStream)`
- But `closeStream()` closes the writer instance’s mutable field (e.g. `channel`) rather than closing the *specific* `fileChannel` that was used when the callback was registered
- Within the same transaction, repeated `open()` calls overwrite the `channel` field as resources are switched
- At transaction completion, the callback may:
  - close only the last channel (leaving earlier channels open), and/or
  - attempt to flush/write using a channel that is already closed, causing `ClosedChannelException`

## Suggested fix direction

To make this safe, the resources created by **a single open()** (e.g. `FileOutputStream`/`FileChannel`/`Writer`/`XMLEventWriter`) should be **encapsulated in a state object**, and the `TransactionAwareBufferedWriter` close callback should be bound to **that specific state instance**.

In short:

- Introduce an `OutputState` in `StaxEventItemWriter` to own those resources
- Register the transactional close callback as `TransactionAwareBufferedWriter(fileChannel, state::closeStream)`
- In `close()`, call `state.close(...)` and then set `state = null`

## Reference / similar design in codebase

`AbstractFileItemWriter` uses an `OutputState` to encapsulate stream/channel lifecycle and binds the transactional writer close callback to that state, avoiding the same class of problems.


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-21

What a fantastic analysis! Thank you very much for doing that and for the PR! Really appreciated 🙏

> Suggested fix direction

> To make this safe, the resources created by a single open() (e.g. FileOutputStream/FileChannel/Writer/XMLEventWriter) should be encapsulated in a state object, and the TransactionAwareBufferedWriter close callback should be bound to that specific state instance.

> In short:

> Introduce an OutputState in StaxEventItemWriter to own those resources
Register the transactional close callback as TransactionAwareBufferedWriter(fileChannel, state::closeStream)
In close(), call state.close(...) and then set state = null
Reference / similar design in codebase

> AbstractFileItemWriter uses an OutputState to encapsulate stream/channel lifecycle and binds the transactional writer close callback to that state, avoiding the same class of problems.

That's it. Making the `StaxEventItemWriter` use the same approach as the `AbstractFileItemWriter` is the way to go. I will check #5177 and get back to you.


