*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# DDLマイグレーションスクリプトの統合テストを追加

**Issue番号**: #4289

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2023-02-08

**ラベル**: type: task, in: core, related-to: ddl-scripts

**URL**: https://github.com/spring-projects/spring-batch/issues/4289

**関連リンク**:
- Commits:
  - [d79971b](https://github.com/spring-projects/spring-batch/commit/d79971b8a5d44e32bb5ea08c6389b2d20b468396)
  - [b095f10](https://github.com/spring-projects/spring-batch/commit/b095f10caa88c68ea72d2b93af02065a754c199a)
  - [45c175b](https://github.com/spring-projects/spring-batch/commit/45c175b1ba2f4a3488e67e5af0546a597789937e)
  - [1f11625](https://github.com/spring-projects/spring-batch/commit/1f11625d35143495603ddedf10aa8d8acfcdd179)
  - [8608e18](https://github.com/spring-projects/spring-batch/commit/8608e18de568e4f54efe886dec56076180d3f1c1)
  - [ced1cbf](https://github.com/spring-projects/spring-batch/commit/ced1cbf246121f85d771b8d851102cb8d1967c46)
  - [01619c6](https://github.com/spring-projects/spring-batch/commit/01619c6f2d4826962162181d96b2837b204a32e1)
  - [b2c63d3](https://github.com/spring-projects/spring-batch/commit/b2c63d3233f6429bb4990f396975b135ca241a38)
  - [9a422fa](https://github.com/spring-projects/spring-batch/commit/9a422fa57cfea2cf1eda7ece09d0bab776cb6d50)

## 内容

#4260 や #4271 のような問題を避けるために、マイグレーションスクリプトを検証する統合テストを作成する必要があります。PostgreSQLの場合は、以下のようなテストが考えられます。



```java

/*

 * Copyright 2020-2023 the original author or authors.

 *

 * Licensed under the Apache License, Version 2.0 (the "License");

 * you may not use this file except in compliance with the License.

 * You may obtain a copy of the License at

 *

 *      https://www.apache.org/licenses/LICENSE-2.0

 *

 * Unless required by applicable law or agreed to in writing, software

 * distributed under the License is distributed on an "AS IS" BASIS,

 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

 * See the License for the specific language governing permissions and

 * limitations under the License.

 */

package org.springframework.batch.core.test.repository;



import org.junit.jupiter.api.Assertions;

import org.junit.jupiter.api.Test;

import org.postgresql.ds.PGSimpleDataSource;

import org.testcontainers.containers.PostgreSQLContainer;

import org.testcontainers.junit.jupiter.Container;

import org.testcontainers.junit.jupiter.Testcontainers;

import org.testcontainers.utility.DockerImageName;



import org.springframework.core.io.ClassPathResource;

import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;



/**

 * @author Mahmoud Ben Hassine

 */

@Testcontainers

class PostgreSQLMigrationScriptIntegrationTests {



	@Container

	public static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(DockerImageName.parse("postgres:13.3"));



	@Test

	void migrationScriptShouldBeValid() {

		PGSimpleDataSource datasource = new PGSimpleDataSource();

		datasource.setURL(postgres.getJdbcUrl());

		datasource.setUser(postgres.getUsername());

		datasource.setPassword(postgres.getPassword());



		ResourceDatabasePopulator databasePopulator = new ResourceDatabasePopulator();

		databasePopulator.addScript(new ClassPathResource("/org/springframework/batch/core/schema-postgresql-4.sql"));

		databasePopulator.addScript(new ClassPathResource("/org/springframework/batch/core/migration/5.0/migration-postgresql.sql"));



		Assertions.assertDoesNotThrow(() -> databasePopulator.execute(datasource));

	}





}



```



組み込みデータベースの場合は、以下のようなテストが考えられます。



```java

/*

 * Copyright 2020-2023 the original author or authors.

 *

 * Licensed under the Apache License, Version 2.0 (the "License");

 * you may not use this file except in compliance with the License.

 * You may obtain a copy of the License at

 *

 *      https://www.apache.org/licenses/LICENSE-2.0

 *

 * Unless required by applicable law or agreed to in writing, software

 * distributed under the License is distributed on an "AS IS" BASIS,

 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

 * See the License for the specific language governing permissions and

 * limitations under the License.

 */

package org.springframework.batch.core.repository;



import org.junit.jupiter.api.Assertions;

import org.junit.jupiter.api.Test;



import org.springframework.core.io.ClassPathResource;

import org.springframework.jdbc.datasource.embedded.EmbeddedDatabase;

import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseBuilder;

import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseType;

import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;



/**

 * @author Mahmoud Ben Hassine

 */

class H2MigrationScriptIntegrationTests {



	@Test

	void migrationScriptShouldBeValid() {

		EmbeddedDatabase embeddedDatabase = new EmbeddedDatabaseBuilder()

				.setType(EmbeddedDatabaseType.H2)

				.addScript("/org/springframework/batch/core/schema-h2-4.sql")

				.addScript("/org/springframework/batch/core/migration/5.0/migration-h2.sql")

				.build();



		Assertions.assertNotNull(embeddedDatabase);

	}





}



```
