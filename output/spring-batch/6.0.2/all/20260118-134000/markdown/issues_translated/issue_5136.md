*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月15日に生成されました）*

# AbstractPaginatedDataItemReaderのjumpToItem(int itemLastIndex)実装がリスタート時の動作を正しく処理しない

**課題番号**: [#5136](https://github.com/spring-projects/spring-batch/issues/5136)

**状態**: open | **作成者**: banseok1216 | **作成日**: 2025-12-05

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5136

## 内容

**バグの説明**

`AbstractPaginatedDataItemReader`の`jumpToItem(int itemLastIndex)`実装は、ステップがリスタートされた際にリーダーの位置を正しく復元しません。実際には、アイテムがスキップされたり、リーダーが予期しない位置から再開されたりします。

このメソッドは、次の`read()`呼び出しで指定されたインデックスのアイテムを返すようにリーダーを位置づけることを意図していますが、現在の実装はそのように動作しません。

### 親クラスの実装

```java
protected void jumpToItem(int itemIndex) throws Exception {
    for (int i = 0; i < itemIndex; i++) {
        read();
    }
}
```

この実装により以下が保証されます:

- `jumpToItem(n)`を呼び出した後、`read()`を呼び出すと**n番目のアイテム**が返される。

---

### AbstractPaginatedDataItemReaderでオーバーライドされた実装

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



主に2つの問題があります:

---

### 1. オフバイワンエラーによる余分な進行

ループ条件が`current >= 0`を使用しているため、イテレータが1回余分に進んでしまいます。
例えば、`jumpToItem(7)`を呼び出すと、次の`read()`は7ではなくインデックス8のアイテムを返します。

| 呼び出し | 期待値 | 実際の値 |
|------|----------|--------|
| `jumpToItem(7)` → `read()` | 7 | 8 |

これは、リーダーが保存されたインデックスから正確に再開すべきという期待に反します。

---

### 2. イテレータがリーダーの状態に割り当てられない

このメソッドはイテレータを進めますが、`results`には割り当てません。次の`read()`呼び出し時に新しいページがロードされ、`jumpToItem`内で行われた位置決め作業がすべて無効になります。これにより、リスタート位置が信頼できなくなり、最初のページが再読み込みされたり、リーダーが間違ったアイテムに到達したりする可能性があります。

---

**環境**

- Spring Batch: 5.x  
- Java: 17  

---

**再現手順**

1. 以下のテストに類似したページネーションリーダーを実装します。
2. `open(new ExecutionContext())`を呼び出します。
3. `jumpToItem(n)`を呼び出します。
4. `read()`を呼び出します。
5. 返される値がインデックス`n`の期待されるアイテムと一致しません。

---

**期待される動作**

`jumpToItem(n)`を呼び出した後、次の`read()`呼び出しはインデックス`n`にあるアイテムを返すべきです。

---

**最小限の完全な再現例**

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
