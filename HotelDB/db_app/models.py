from django.db import models


class Admins(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=100)
    full_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "Админ: " + self.username

    class Meta:
        managed = False
        db_table = "admins"


class Bookings(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("Users", on_delete=models.CASCADE)  # Добавлено CASCADE
    room = models.ForeignKey("Rooms", on_delete=models.CASCADE)  # Добавлено CASCADE
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "Бронь №" + str(self.room)

    class Meta:
        managed = False
        db_table = "bookings"


class RoomImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    room = models.ForeignKey("Rooms", on_delete=models.CASCADE)  # Добавлено CASCADE
    image_path = models.ImageField(upload_to="rooms", blank=True, null=True)

    def __str__(self):
        return "Картинка " + str(self.room)

    class Meta:
        managed = False
        db_table = "room_images"


class Rooms(models.Model):
    room_id = models.AutoField(primary_key=True)
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    capacity = models.IntegerField()

    def __str__(self):
        return "Комната №" + self.room_number

    class Meta:
        managed = False
        db_table = "rooms"


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=100)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return "Пользователь: " + self.username

    class Meta:
        managed = False
        db_table = "users"
