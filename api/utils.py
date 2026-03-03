import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from .models import ScamDataset, ModelStatus
from django.utils import timezone


def retrain_model():
    data = ScamDataset.objects.all()

    if data.count() < 2:
        return 0

    texts = [d.text for d in data]
    labels = [d.label for d in data]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    model = LogisticRegression()
    model.fit(X, labels)

    predictions = model.predict(X)
    accuracy = accuracy_score(labels, predictions)
    accuracy_percent = round(accuracy * 100, 2)

    # Save model
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open("vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    # Save accuracy to DB
    status, created = ModelStatus.objects.get_or_create(id=1)
    status.accuracy = accuracy_percent
    status.last_trained = timezone.now()
    status.save()

    print(f"Model retrained successfully. Accuracy: {accuracy_percent}%")

    return accuracy_percent