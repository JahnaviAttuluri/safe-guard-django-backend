from django.db import models


class ScamDataset(models.Model):
    text = models.TextField()
    label = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]


class ModelStatus(models.Model):
    accuracy = models.FloatField(default=0.0)
    last_trained = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Accuracy: {self.accuracy}%"
class DatasetUpload(models.Model):
    csv_file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upload {self.id}"