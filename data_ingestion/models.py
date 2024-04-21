from django.db import models

# Create your models here.
class Object(models.Model):
    object_id = models.AutoField(primary_key=True,unique=True)
    name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=30)
    ra = models.FloatField()
    dec = models.FloatField()

    # Set constrain for not having the same object repited
    class Meta:
        unique_together = ('ra', 'dec')



    def __str__(self):
        return str(self.object_id)


class Spect(models.Model):
    STATE_CHOICES = (
        ('soft', 'Soft'),
        ('intermediate', 'Intermediate'),
        ('hard', 'Hard'),
     )    
   
    spect_id = models.AutoField(primary_key=True, unique=True)
    # Foreing key with Object model
    object = models.ForeignKey(Object, on_delete=models.CASCADE)

    # Requiered fiels
    exptime = models.FloatField()
    min_wavelenght = models.FloatField()
    max_wavelenght = models.FloatField()
    header = models.TextField()
    jd = models.FloatField()
    hjd = models.FloatField()
    file = models.FileField()
    index = models.IntegerField()

    # Optional field
    sn = models.FloatField(null=True, blank=True)
    instrument = models.CharField(max_length=30,null=True, blank=True)
    outburts = models.BooleanField(null=True, blank=True)
    ob = models.IntegerField(null=True, blank=True)
    state = models.CharField(max_length=12, choices=STATE_CHOICES, default='soft')
    flux_calibrated = models.BooleanField(null=True, blank=True)
    spect_resolution = models.FloatField(null=True, blank=True)

    # Method for converting jd to mjd
    @property
    def mjd(self):
        return self.jd - 2400000.5


    # Set constrain for not ingesting the same spectra twice
    class Meta:
        unique_together = ('object','jd') # TODO add instrument


    def __str__(self):
        return str(self.spect_id)
