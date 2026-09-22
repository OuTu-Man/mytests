# My Tests

## Blog

    > 迁移数据库:

    ```shell
    python manage.py makemigrations
    python manage.py migrate
    ```

    > 创建超级用户:

    ```shell
    python manage.py createsuperuser
    ```

    > 运行开发服务器

    ```shell
    python manage.py runserver
    ```

## Dockerfile

    > 构建镜像

    ```shell
    docker build -t my-app .
    docker run -d --name my-app -p 8000:8000 my-app
    ```
