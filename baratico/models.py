from django.db import models
from django.db import connection
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

    def calcular_total(self):
        id_factura = self.id
        stringsql = ''' SELECT SUM(l.cantidad * p.precio)
                        FROM baratico_lineafacturaproducto l
                          INNER JOIN baratico_producto p ON l.producto_id = p.id
                        WHERE l.factura_id = %s
         '''

        cursor = connection.cursor()
        cursor.execute(stringsql, [id_factura])

        row = cursor.fetchone()

        if row[0]:
            return row[0].real
        else:
            return 0


class LineaFacturaOferta(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    oferta = models.ForeignKey('Oferta', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('factura', 'oferta'),)

    def __str__(self):
        return 'ID: ' + self.factura.id.__str__() + self.oferta.id.__str__() + self.id.__str__()


class LineaFacturaProducto(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('factura', 'producto'),)

    def __str__(self):
        return 'ID:' + self.factura.id.__str__() + self.id.__str__()


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
    imagen = models.ImageField(upload_to='imagenes/')
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=16, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def calificacion_general(self):
        qs = Resenna.objects.filter(producto=self.id)
        calificacion = 0

        for tupla in qs:
            calificacion += tupla.calificacion

        if qs.count() > 0:
            return calificacion / qs.count()
        else:
            return 0.0

    def ventas_totales(self):
        stringsql = '''SELECT sum(sumas.c) FROM (
                       (
                       SELECT sum(lfp.cantidad) AS c
                       FROM baratico_producto p 
                           INNER JOIN baratico_lineafacturaproducto lfp ON (p.id = lfp.producto_id)
                       WHERE p.id = %s
                       )
                       UNION
                       (
                       SELECT sum(lfo.cantidad * po.cantidad) as c
                       FROM baratico_lineafacturaoferta lfo 
                           INNER JOIN baratico_productooferta po ON (lfo.oferta_id = po.oferta_id AND 
                                                                     po.producto_id = %s)
                       )
                       )sumas
                       '''
        cursor = connection.cursor()
        cursor.execute(stringsql, [self.id, self.id])

        row = cursor.fetchone()
        return row

    def __str__(self):
        return self.nombre


class ProductoOferta(models.Model):
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('oferta', 'producto'),)

    def __str__(self):
        return self.producto.nombre


class Resenna(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    calificacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    comentario = models.CharField(max_length=1000,blank=True)
    fecha = models.DateField(auto_now_add=True)  # auto_now_add: Guarda la fecha actual automaticamente

    class Meta:  # Metadatos sobre el modelo. En este caso se usan para hacer un unique key de varias columnas
        unique_together = (('usuario', 'producto'),)

    def get_nombre_producto(self):
        return self.producto.nombre


class Usuario(models.Model):  # Clase modelo que extiende los datos del modelo de Usuario (User) de Django.
    nombre_usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=500)

    def get_total_productos(self):
        id_user = self.nombre_usuario.id
        stringsql = '''SELECT SUM(cp.cantidad * p.precio)
                       FROM baratico_carritoproducto cp
                       INNER JOIN baratico_producto p ON cp.producto_id = p.id
                       WHERE cp.usuario_id = %s
                       '''
        cursor = connection.cursor()
        cursor.execute(stringsql, [id_user])

        row = cursor.fetchone()

        if row[0]:
            return row[0].real
        else:
            return 0

    def __str__(self):
        return self.nombre_usuario.get_username()
