# Spring Framework 6.0.0-M3 課題サマリー一覧

## 概要

このドキュメントは、Spring Framework 6.0.0-M3で対応された34の課題を分類し、簡潔にまとめたものです。詳細な技術解説が必要な主要課題については、個別のサマリードキュメントを参照してください。

## 詳細サマリー作成済み課題

以下の課題については、PlantUML図解、背景知識、コード例を含む詳細なサマリーを作成しました:

1. **issue_22609_bean_overloading.md**: @Beanメソッドのオーバーロードによる条件不一致問題
2. **issue_27416_dependencies.md**: 依存関係のアップグレード(AspectJ, Kotlin, Groovy, Gradle)
3. **issue_27828_aot_infrastructure.md**: AOT(Ahead-of-Time)コンパイル基盤の構築
4. **issue_27866_core_improvements.md**: コアAPI改善とクリーンアップ

## 課題分類

### 1. AOT関連課題(AOT Infrastructure)

AOT(Ahead-of-Time)コンパイル機能の実装に関連する課題群。

| Issue | タイトル | 概要 | 重要度 |
|-------|---------|------|--------|
| #27828 | JavaPoetのリパッケージング | コード生成ライブラリの統合 | ⭐⭐⭐ |
| #27829 | Runtime Hints登録API | GraalVM設定のプログラム的記述 | ⭐⭐⭐ |
| #27921 | AOT版AutowiredAnnotationBeanPostProcessor | @Autowired処理のAOT対応 | ⭐⭐⭐ |
| #28028 | コアJavaPoetユーティリティ | コード生成の共通処理 | ⭐⭐ |
| #28030 | コード貢献インフラ | コード生成フレームワーク | ⭐⭐⭐ |
| #28047 | Beanインスタンス化ジェネレーター | Bean登録コードの自動生成 | ⭐⭐⭐ |
| #28065 | ApplicationContext AOT処理 | コンテキスト初期化の最適化 | ⭐⭐⭐ |
| #28088 | ApplicationContextセットアップAPI | コンテキスト構成への貢献API | ⭐⭐ |
| #28111 | AOTでのImportAwareサポート | @Import処理のAOT対応 | ⭐⭐ |
| #28120 | 生成コードのコンパイル/実行 | テスト基盤 | ⭐⭐ |
| #28148 | 生成コード用Runtime Hints | AOTとRuntime Hintsの統合 | ⭐⭐⭐ |
| #28149 | GeneratedType基盤 | 生成コードの型管理 | ⭐⭐ |
| #28150 | ApplicationContextAotGenerator導入 | AOT処理の統合API | ⭐⭐⭐ |
| #28151 | AOTでの複数init/destroyメソッド対応 | ライフサイクル処理の更新 | ⭐⭐ |

**AOTの目的**: Spring ApplicationをGraalVM Native Imageとしてコンパイルし、起動時間を数秒から数十ミリ秒に短縮。

### 2. 依存関係アップグレード(Dependency Upgrades)

Java 17対応とライブラリの最新化。

| Issue | タイトル | アップグレード内容 | 理由 |
|-------|---------|-----------------|------|
| #27416 | AspectJ 1.9.8 GA | AspectJ 1.9.7 → 1.9.8 | Java 17正式サポート |
| #27814 | Kotlinバイトコードレベル | Kotlin 1.5.x → 1.6.20 | Java 17バイトコード対応 |
| #27985 | Groovy 4.0 | Groovy 3.x → 4.0 | Java 17サポート |
| #28020 | Gradle 7.4 | Gradle 7.3.3 → 7.4 | ビルドツール最新化 |
| #28147 | Kotlin 1.6.20-RC | Kotlin 1.6.20-RCへの更新 | 新機能とバグ修正 |

### 3. Bean定義とライフサイクル(Bean Definition & Lifecycle)

Bean登録、オーバーライド、ライフサイクル管理の改善。

| Issue | タイトル | 概要 | カテゴリ |
|-------|---------|------|---------|
| #22609 | @Beanメソッドのオーバーロード問題 | 条件付きBean定義のオーバーロード | バグ修正 |
| #27866 | Bean名/エイリアスオーバーライド一貫性 | Bean名とエイリアスの競合処理 | バグ修正 |
| #28013 | 複数init/destroyメソッド対応 | 複数のライフサイクルメソッド | AOT拡張 |
| #28029 | BeanDefinitionValueResolverの公開 | 内部APIの公開 | API改善 |
| #28093 | Inner Bean用MergedBeanDefinitionの合理化 | 内部Bean処理の改善 | 最適化 |
| #28153 | BeanRegistration用RootBeanDefinition | Bean登録の型安全性向上 | AOT改善 |
| #28154 | コンストラクタの曖昧性チェック | コンストラクタ選択ロジック改善 | バグ修正 |

### 4. テスト関連(Testing)

テストインフラの改善とクリーンアップ。

| Issue | タイトル | 概要 | 影響 |
|-------|---------|------|------|
| #28054 | 非推奨SocketUtilsの削除 | ポート検索ユーティリティの削除 | 代替手段必要 |
| #28120 | 生成コードのコンパイル/実行 | AOTテスト基盤 | テスト改善 |

### 5. Web/WebFlux関連(Web & WebFlux)

Web機能の改善とKotlin対応。

| Issue | タイトル | 概要 | フレームワーク |
|-------|---------|------|-------------|
| #28098 | 型安全なトランザクションロールバックルール | トランザクション制御の改善 | TX管理 |
| #28144 | KotlinBodySpecの置換 | Kotlin WebFlux API改善 | WebFlux |
| #28146 | WebSocketConfigurationSupportの型公開 | WebSocket設定の改善 | WebSocket |

### 6. Hibernate/JPA関連(Hibernate & JPA)

Hibernate 6対応。

| Issue | タイトル | 概要 | バージョン |
|-------|---------|------|----------|
| #28007 | HibernateJpaDialectのHibernate 6互換性 | Hibernate 6.0サポート | Hibernate 6.0 |

### 7. ビルド/開発ツール(Build & Development Tools)

ビルドプロセスとドキュメント生成の改善。

| Issue | タイトル | 概要 | ツール |
|-------|---------|------|--------|
| #27928 | Gradle apiDiffタスクのマイルストーン対応 | API差分検出の改善 | Gradle |

### 8. アノテーション/リフレクション(Annotations & Reflection)

アノテーション処理とリフレクション機能の改善。

| Issue | タイトル | 概要 | 影響 |
|-------|---------|------|------|
| #28079 | Enclosing Class検索戦略の非推奨化 | アノテーション検索の明確化 | 非推奨化 |

### 9. エラーハンドリング(Error Handling)

RFC 7807 Problem Details対応。

| Issue | タイトル | 概要 | 標準 |
|-------|---------|------|------|
| #28187 | RFC 7807 Problem Details型と例外 | 標準化されたエラーレスポンス | RFC 7807 |

**RFC 7807とは**: HTTPエラーレスポンスの標準化仕様。JSON形式で構造化されたエラー情報を返す。

```json
{
  "type": "https://example.com/probs/out-of-credit",
  "title": "You do not have enough credit.",
  "status": 403,
  "detail": "Your current balance is 30, but that costs 50.",
  "instance": "/account/12345/msgs/abc"
}
```

## 技術カテゴリ別統計

| カテゴリ | 課題数 | 割合 |
|---------|-------|------|
| AOT関連 | 14 | 41% |
| Bean管理 | 7 | 21% |
| 依存関係アップグレード | 5 | 15% |
| Web/WebFlux | 3 | 9% |
| その他 | 5 | 14% |

## 重要な概念の説明

### AOT(Ahead-of-Time)コンパイル

**従来(JIT: Just-In-Time)**
```
起動 → クラススキャン(1-2秒) → リフレクション処理(0.5-1秒) → 実行
```

**AOT**
```
ビルド時: コード生成(事前処理)
実行時: 生成済みコード実行(< 100ms) → 実行
```

**利点**
- 起動時間: 20-40倍高速化
- メモリ使用量: 約1/4に削減
- GraalVM Native Image対応

### GraalVM Native Image

Javaアプリケーションをネイティブバイナリにコンパイルする技術。

**メリット**
- 超高速起動(数十ミリ秒)
- 小さなメモリフットプリント
- コンテナに最適

**制約**
- リフレクションは事前宣言が必要
- 動的プロキシは事前設定が必要
- すべてのライブラリが対応しているわけではない

### Runtime Hints

GraalVMに対して、リフレクション/プロキシ/リソースの使用を事前に伝える仕組み。

```java
@ImportRuntimeHints(MyHints.class)
public class AppConfig {
    // ...
}

class MyHints implements RuntimeHintsRegistrar {
    @Override
    public void registerHints(RuntimeHints hints, ClassLoader classLoader) {
        hints.reflection()
            .registerType(UserService.class, MemberCategory.INVOKE_DECLARED_CONSTRUCTORS);
        hints.resources()
            .registerPattern("application*.yml");
    }
}
```

## 開発者への影響まとめ

### 必須対応

| 項目 | 内容 |
|------|------|
| JDK要件 | JDK 17以上 |
| AspectJ | 1.9.8以上 |
| Kotlin | 1.6.20以上(Kotlinを使用する場合) |

### 非推奨機能

| 機能 | 代替手段 |
|------|---------|
| `SocketUtils` | ポート0(OS自動割り当て) |
| `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES` | カスタム検索ロジック |

### 新機能

| 機能 | 説明 | 対象 |
|------|------|------|
| AOT処理 | Native Image対応 | すべてのアプリ(オプション) |
| Runtime Hints | GraalVM設定API | Native Imageユーザー |
| 複数init/destroyメソッド | ライフサイクル強化 | 内部/AOT用 |
| RFC 7807対応 | 標準化エラーレスポンス | Web API開発者 |

## マイグレーションチェックリスト

### 1. 環境準備
- [ ] JDK 17にアップグレード
- [ ] Spring Framework 6.0.0-M3に更新
- [ ] AspectJ 1.9.8に更新(使用している場合)
- [ ] Kotlin 1.6.20に更新(使用している場合)

### 2. コード変更
- [ ] `SocketUtils`を使用している箇所を修正
- [ ] `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES`を使用している箇所を確認
- [ ] Bean名/エイリアスの競合がないか確認

### 3. テスト
- [ ] すべてのテストが通ることを確認
- [ ] Bean定義のオーバーライド警告を確認
- [ ] AOT処理を試す(オプション)

### 4. Native Image対応(オプション)
- [ ] Spring Boot 3.0+を使用
- [ ] Native Imageビルドツールを設定
- [ ] Runtime Hintsを追加(必要に応じて)
- [ ] Native Imageビルドとテスト

## 参考リソース

- **Spring Framework 6.0ドキュメント**: https://docs.spring.io/spring-framework/docs/6.0.x/reference/html/
- **GraalVM Native Image**: https://www.graalvm.org/latest/reference-manual/native-image/
- **Spring Boot 3.0**: https://spring.io/projects/spring-boot
- **AspectJ 1.9.8リリースノート**: https://www.eclipse.org/aspectj/

## まとめ

Spring Framework 6.0.0-M3は、Java 17ベースラインとAOT/GraalVM Native Image対応により、クラウドネイティブ時代に最適化されたフレームワークとなりました。既存のSpringアプリケーションは基本的にそのまま動作しますが、Native Imageとして実行することで、起動時間とメモリ使用量を劇的に改善できます。

### 主な成果
- **AOT基盤**: 14の課題で包括的なAOT処理機能を実装
- **Java 17対応**: 最新Java機能の完全サポート
- **API改善**: Bean管理、ライフサイクル、エラーハンドリングの強化
- **クリーンアップ**: 非推奨機能の削除と一貫性の向上

Spring Framework 6.0は、既存の開発体験を維持しながら、次世代のクラウドネイティブアプリケーション開発を可能にします。
