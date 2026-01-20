# The implementation of jumpToItem(int itemLastIndex) in AbstractPaginatedDataItemReader does not handle restart behavior correctly.

**Issue番号**: #5136

**状態**: closed | **作成者**: banseok1216 | **作成日**: 2025-12-05

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5136

**関連リンク**:
- Commits:
  - [d5fbb54](https://github.com/spring-projects/spring-batch/commit/d5fbb5493b78844fc8f8cf03a5eaafca380b34e1)

## 内容

**Bug description**

The `jumpToItem(int itemLastIndex)` implementation in `AbstractPaginatedDataItemReader` does not correctly restore the reader position when a step is restarted. In practice, this leads to skipped items or the reader resuming from an unexpected location.

While the method is intended to position the reader so that the next call to `read()` returns the item at the given index, the current implementation does not behave that way.

### Parent class implementation

```java
protected void jumpToItem(int itemIndex) throws Exception {
    for (int i = 0; i < itemIndex; i++) {
        read();
    }
}
```

This implementation ensures:

- After calling `jumpToItem(n)`, invoking `read()` returns the **nth item**.

---

### Overridden implementation in AbstractPaginatedDataItemReader

```java
@Override
protected void jumpToItem(int itemLastIndex) throws Exception {
    this.lock.lock();
    try {
        page = itemLastIndex / pageSize;
        int current = itemLastIndex % pageSize;

        Iterator<T> initialPage = doPageRead();

        for (; current >= 0; current--) {
            initialPage.next();
        }
    }
    finally {
        this.lock.unlock();
    }
}
```



There are two main issues:

---

### 1. Off-by-one advancement

Because the loop condition uses `current >= 0`, the iterator advances one time too many.  
For example, calling `jumpToItem(7)` causes the next `read()` to return the item at index 8 instead of 7.

| Call | Expected | Actual |
|------|----------|--------|
| `jumpToItem(7)` → `read()` | 7 | 8 |

This breaks the expectation that the reader should restart exactly at the stored index.

---

### 2. Iterator not assigned to the reader state

The method advances an iterator but never assigns it to `results`. On the next `read()` call, a new page is loaded, undoing any positioning work done inside `jumpToItem`. This makes the restart position unreliable and can result in the first page being re-read or the reader landing on the wrong item.

---

**Environment**

- Spring Batch: 5.x  
- Java: 17  

---

**Steps to reproduce**

1. Implement a paginated reader similar to the one in the test below.
2. Call `open(new ExecutionContext())`.
3. Invoke `jumpToItem(n)`.
4. Call `read()`.
5. The value returned will not match the expected item at index `n`.

---

**Expected behavior**

After calling `jumpToItem(n)`, the following `read()` call should return the item located at index `n`.

---

**Minimal Complete Reproducible example**

```java
package org.springframework.batch.infrastructure.item.data;

import org.junit.jupiter.api.Test;
import org.springframework.batch.infrastructure.item.ExecutionContext;

import java.util.Iterator;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class AbstractPaginatedDataItemReaderTests {

  static class PaginatedDataItemReader extends AbstractPaginatedDataItemReader<Integer> {

    private final List<Integer> data = List.of(
        0,1,2,3,4,5,6,7,8,9,
        10,11,12,13,14,15,16,17,18,19
    );

    @Override
    protected Iterator<Integer> doPageRead() {
      int start = page * pageSize;
      int end = Math.min(start + pageSize, data.size());
      return data.subList(start, end).iterator();
    }
  }

  @Test
  void jumpToItem_shouldReadExactItem_afterJump() throws Exception {
    PaginatedDataItemReader reader = new PaginatedDataItemReader();
    reader.open(new ExecutionContext());

    reader.jumpToItem(7);

    Integer value = reader.read();
    assertEquals(7, value);
  }

  @Test
  void jumpToItem_zeroIndex() throws Exception {
    PaginatedDataItemReader reader = new PaginatedDataItemReader();
    reader.open(new ExecutionContext());

    reader.jumpToItem(0);

    Integer value = reader.read();
    assertEquals(0, value);
  }

  @Test
  void jumpToItem_lastItemInPage() throws Exception {
    PaginatedDataItemReader reader = new PaginatedDataItemReader();
    reader.open(new ExecutionContext());

    reader.jumpToItem(9);

    Integer value = reader.read();
    assertEquals(9, value);
  }

  @Test
  void jumpToItem_firstItemOfNextPage() throws Exception {
    PaginatedDataItemReader reader = new PaginatedDataItemReader();
    reader.open(new ExecutionContext());

    reader.jumpToItem(10);

    Integer value = reader.read();
    assertEquals(10, value);
  }

}
```

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-15

Thank you for reporting this issue and for contributing a fix!

