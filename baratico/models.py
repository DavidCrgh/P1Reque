from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator


class CarritoOferta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    oferta = models.ForeignKey('Oferta', on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('usuario', 'oferta'),)


class CarritoProducto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('usuario', 'producto'),)


class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    supercategoria = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.supercategoria is not None:
            return '[{0}] {1}'.format(self.supercategoria.nombre, self.nombre)
        return self.nombre


class Factura(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)  # auto_now_add: Guarda la fecha actual automaticamente
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)


class LineaFacturaOferta(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    oferta = models.ForeignKey('Oferta', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('factura', 'oferta'),)


class LineaFacturaProducto(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('factura', 'producto'),)


class Oferta(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    precio = models.DecimalField(max_digits=16, decimal_places=2)
    # region Definicion de Tipo
    DESCUENTO = 'D'
    PAQUETE = 'P'
    TIPO_OFERTA_CHOICES = (
        (DESCUENTO, 'Descuento'),
        (PAQUETE, 'Paquete'),
    )
    tipo = models.CharField(max_length=1, choices=TIPO_OFERTA_CHOICES)
    # endregion

    def es_descuento(self):
        return self.tipo == self.DESCUENTO

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=1000)
    imagen = models.ImageField()
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=16, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class ProductoOferta(models.Model):
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('oferta', 'producto'),)


class Resenna(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    calificacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    comentario = models.CharField(max_length=1000)
    fecha = models.DateField(auto_now_add=True)  # auto_now_add: Guarda la fecha actual automaticamente

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('usuario', 'producto'),)


class Usuario(models.Model):  # Clase modelo que extiende los datos del modelo de Usuario (User) de Django.
    nombre_usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=500)
