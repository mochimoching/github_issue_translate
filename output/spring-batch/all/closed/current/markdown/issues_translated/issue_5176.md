*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月26日に生成されました）*

# 同一トランザクション内で複数回リソースを切り替えた際にClosedChannelExceptionとFileChannelのリークが発生する

**Issue番号**: [#5176](https://github.com/spring-projects/spring-batch/issues/5176)

**状態**: closed | **作成者**: banseok1216 | **作成日**: 2025-12-20

**ラベル**: status: duplicate

**URL**: https://github.com/spring-projects/spring-batch/issues/5176

## 内容

## バグの説明

`StaxEventItemWriter`を**同一トランザクション（TransactionTemplate）内**で以下のパターンで使用すると、問題が発生します：

- 同じ`StaxEventItemWriter`インスタンスを使用
- `setResource(r1) -> open -> write -> close`
- `setResource(r2) -> open -> write -> close`
- `setResource(r3) -> open -> write -> close`

観測される問題（環境によって、片方または両方が発生する可能性があります）：

1) トランザクションコミット時（またはトランザクション同期の終了時）に`java.nio.channels.ClosedChannelException`が発生
2) r1/r2/r3用に開かれた`FileChannel`の一部が、トランザクション終了後も開いたまま残る（リソースリーク）

関連Issue：
- https://github.com/spring-projects/spring-batch/issues/5098

## 環境

- Spring Batchバージョン: 6.0.x、5.2.x

## 再現手順

1. Spring Batchのコードベースの`org.springframework.batch.infrastructure.item.xml.TransactionalStaxEventItemWriterTests`に以下の2つのテストを追加します。
2. テストを実行します。以下のいずれかが観測されます：
   - `shouldWriteThreeSeparateFilesWhenMultipleOpenCloseAndResourceSwitchInSingleTransaction`で`ClosedChannelException`が発生
   - `shouldCloseAllFileChannelsAfterTransaction`でトランザクション完了後も一部のチャネルが`isOpen() == true`のままとなり失敗

## 期待される動作

同一トランザクション内でリソースを切り替え、ライターを複数回open/closeしても：

1) トランザクション完了時に`ClosedChannelException`がスローされないこと
2) トランザクション終了（コミット/ロールバック）後、**そのトランザクション中に開かれたすべてのFileChannelがクローズされていること**

## 最小限の再現可能なサンプル

以下のテストは2つの側面を検証します：

1) 例外の再現: `shouldWriteThreeSeparateFilesWhenMultipleOpenCloseAndResourceSwitchInSingleTransaction`
2) リークの再現: `shouldCloseAllFileChannelsAfterTransaction`
   - リフレクションを使用して内部の`FileChannel`を取得し、トランザクション後に`isOpen()`をチェックします。

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
        // 例外が発生してもリークのチェックを続行
    }

    assertEquals(3, opened.size(), "Expected 3 opened channels");
    for (FileChannel ch : opened) {
        assertFalse(ch.isOpen(), "FileChannel should be closed after transaction");
    }
}

private static FileChannel extractChannelFromStaxWriter(StaxEventItemWriter<?> w) throws Exception {
    // レガシーバージョン
    Field field = StaxEventItemWriter.class.getDeclaredField("channel");
    field.setAccessible(true);
    return (FileChannel) field.get(w);
    
    // 改善版
    // Spring Batch 6.xのレイアウト: StaxEventItemWriter.state.channel
    Field stateField = StaxEventItemWriter.class.getDeclaredField("state");
    stateField.setAccessible(true);
    Object state = stateField.get(w);
    Field channelField = state.getClass().getDeclaredField("channel");
    channelField.setAccessible(true);
    return (FileChannel) channelField.get(state);
}
```

## 観測されるスタックトレースの例

```text
org.springframework.batch.infrastructure.support.transaction.FlushFailedException: Could not write to output buffer
Caused by: java.nio.channels.ClosedChannelException
```

## この問題が発生する理由

重要なのは、`TransactionAwareBufferedWriter`が**トランザクション同期時にフラッシュ/クローズを実行する**という点です。

問題のある構造：

- `TransactionAwareBufferedWriter(fileChannel, this::closeStream)`のようにクローズコールバックを登録している
- しかし、`closeStream()`はコールバック登録時に使用された*特定の*`fileChannel`ではなく、ライターインスタンスのミュータブルなフィールド（例：`channel`）をクローズする
- 同一トランザクション内で、リソースが切り替わるたびに`open()`が呼び出されると`channel`フィールドが上書きされる
- トランザクション完了時、コールバックは以下のいずれか（または両方）を引き起こす可能性がある：
  - 最後のチャネルのみをクローズする（それ以前のチャネルは開いたまま残る）
  - 既にクローズされているチャネルを使用してフラッシュ/書き込みを試み、`ClosedChannelException`が発生する

## 推奨される修正方針

これを安全にするには、**1回のopen()で作成されたリソース**（例：`FileOutputStream`/`FileChannel`/`Writer`/`XMLEventWriter`）を**状態オブジェクトにカプセル化**し、`TransactionAwareBufferedWriter`のクローズコールバックを**その特定の状態インスタンスにバインド**する必要があります。

つまり：

- `StaxEventItemWriter`に`OutputState`を導入してこれらのリソースを所有させる
- トランザクションのクローズコールバックを`TransactionAwareBufferedWriter(fileChannel, state::closeStream)`として登録
- `close()`では`state.close(...)`を呼び出してから`state = null`を設定

## 参考 / コードベース内の類似設計

`AbstractFileItemWriter`は`OutputState`を使用してストリーム/チャネルのライフサイクルをカプセル化し、トランザクション対応ライターのクローズコールバックをその状態にバインドすることで、同種の問題を回避しています。


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-21

素晴らしい分析ですね！この分析とPRを作成していただき、本当にありがとうございます！大変感謝しています 🙏

> 推奨される修正方針

> これを安全にするには、1回のopen()で作成されたリソース（例：FileOutputStream/FileChannel/Writer/XMLEventWriter）を状態オブジェクトにカプセル化し、TransactionAwareBufferedWriterのクローズコールバックをその特定の状態インスタンスにバインドする必要があります。

> つまり：

> StaxEventItemWriterにOutputStateを導入してこれらのリソースを所有させる
トランザクションのクローズコールバックをTransactionAwareBufferedWriter(fileChannel, state::closeStream)として登録
close()ではstate.close(...)を呼び出してからstate = nullを設定
参考 / コードベース内の類似設計

> AbstractFileItemWriterはOutputStateを使用してストリーム/チャネルのライフサイクルをカプセル化し、トランザクション対応ライターのクローズコールバックをその状態にバインドすることで、同種の問題を回避しています。

その通りです。`StaxEventItemWriter`を`AbstractFileItemWriter`と同じアプローチに変更するのが正しい方向性です。[#5177](https://github.com/spring-projects/spring-batch/issues/5177)を確認して、改めてご連絡します。
