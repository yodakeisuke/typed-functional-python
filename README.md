## この記事のサンプルリポジトリ
https://zenn.dev/kei1104/articles/b6a909a60e0138

### up

```
docker compose up -d
```

### API
http://localhost:8080/
http://localhost:8080/items/5?q=somequery

### docs
http://localhost:8080/docs#/


# down
```
docker compose down
```

## poetry

```terminal
docker compose exec api /bin/bash
```

```root@19c309553d08:/app#
poetry add requests
```
