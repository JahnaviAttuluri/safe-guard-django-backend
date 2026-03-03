from django.contrib import admin
from .models import ScamDataset, ModelStatus, DatasetUpload
from .utils import retrain_model
import csv


# ---------------------------
# RETRAIN ACTION
# ---------------------------
@admin.action(description="Retrain ML Model")
def retrain_selected(modeladmin, request, queryset):
    accuracy = retrain_model()

    modeladmin.message_user(
        request,
        f"Model retrained successfully. Accuracy: {accuracy}%"
    )


# ---------------------------
# SCAM DATASET ADMIN
# ---------------------------
@admin.register(ScamDataset)
class ScamDatasetAdmin(admin.ModelAdmin):
    list_display = ("text", "label", "uploaded_at")
    actions = [retrain_selected]


# ---------------------------
# MODEL STATUS ADMIN
# ---------------------------
@admin.register(ModelStatus)
class ModelStatusAdmin(admin.ModelAdmin):
    list_display = ("accuracy", "last_trained")


# ---------------------------
# DATASET UPLOAD ADMIN
# ---------------------------
@admin.register(DatasetUpload)
class DatasetUploadAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_at")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        file_path = obj.csv_file.path

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                text = row.get("description", "")
                label = int(row.get("fraudulent", 0))

                # Avoid empty rows
                if text.strip() != "":
                    ScamDataset.objects.create(
                        text=text,
                        label=label
                    )

        # Automatically retrain after upload
        accuracy = retrain_model()

        self.message_user(
            request,
            f"CSV uploaded successfully. Model retrained. Accuracy: {accuracy}%"
        )