from sgo import models


class Movie(models.Model):
    title = models.CharField('标题', max_length=50)
    description = models.CharField('电影描述', max_length=60)


class Author(models.Model):
    name = models.CharField('标题', max_length=50)
    sex = models.BooleanField('性别')

    class Meta:
        table_name = 'Authors'


if __name__ == '__main__':
    print(Movie.table_name)
