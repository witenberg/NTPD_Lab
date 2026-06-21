# Politechnika Bydgoska im. Jana i Jędrzeja Śniadeckich
Wydział Telekomunikacji,  
Informatyki i Elektrotechniki  
Nowoczesne Technologie Przetwarzania Danych  
Laboratorium 13  
Temat: Orkiestracja kontenerów w Kubernetes - wdrożenie API modelu ML na lokalnym klastrze


## Cel ćwiczenia

Celem ćwiczenia jest praktyczne poznanie orkiestracji kontenerów w Kubernetes; uruchomienie lokalnego klastra; wdrożenie skonteneryzowanego API modelu ML (z wcześniejszych laboratoriów) jako Deployment i Service; skalowanie aplikacji; wykonanie aktualizacji kroczącej (rolling update) i wycofania zmian (rollback); skonfigurowanie sond zdrowia oraz limitów zasobów. Laboratorium pokazuje, jak przejść od pojedynczego kontenera Docker do zarządzanego, skalowalnego i samonaprawiającego się wdrożenia.

## Materiały

https://kubernetes.io/docs/home/  
https://minikube.sigs.k8s.io/docs/start/  
https://kind.sigs.k8s.io/docs/user/quick-start/  
https://kubernetes.io/docs/reference/kubectl/  
https://docs.docker.com/

## Zadanie 1: Przygotowanie środowiska

- Zainstaluj `kubectl` oraz lokalny klaster Kubernetes (Minikube albo kind; można też użyć Kubernetes wbudowanego w Docker Desktop).

- Uruchom klaster i sprawdź, czy działa.

- W sprawozdaniu podaj wersję Kubernetes oraz sposób uruchomienia klastra.

Przykład startowy:

```bash
minikube start
kubectl get nodes
kubectl cluster-info
```

## Zadanie 2: Obraz kontenera modelu ML

- Wykorzystaj API modelu ML z wcześniejszych laboratoriów (LAB03/LAB04) lub przygotuj prostą aplikację z endpointem `/predict` oraz endpointem zdrowia (np. `/health`).

- Zbuduj obraz Dockera aplikacji.

- Załaduj obraz do lokalnego klastra, aby Kubernetes nie próbował pobierać go z zewnętrznego rejestru.

- W sprawozdaniu podaj nazwę i tag obrazu.

Przykład startowy:

```bash
docker build -t ml-api:1.0 .

# Minikube:
minikube image load ml-api:1.0

# kind:
# kind load docker-image ml-api:1.0
```

## Zadanie 3: Deployment i Service

- Przygotuj manifest `Deployment` uruchamiający aplikację w kilku replikach.

- Przygotuj manifest `Service`, który udostępni aplikację wewnątrz klastra i na zewnątrz.

- Zastosuj manifesty i sprawdź, czy pody działają.

- Uzyskaj adres usługi i przetestuj endpoint predykcji.

Przykład startowy (`deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ml-api
  template:
    metadata:
      labels:
        app: ml-api
    spec:
      containers:
        - name: ml-api
          image: ml-api:1.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
```

Przykład startowy (`service.yaml`):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ml-api
spec:
  type: NodePort
  selector:
    app: ml-api
  ports:
    - port: 80
      targetPort: 8000
```

Zastosowanie i test:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get pods
minikube service ml-api --url
```

## Zadanie 4: Skalowanie, aktualizacja krocząca i rollback

- Zmień liczbę replik aplikacji i sprawdź, że Kubernetes utrzymuje zadaną liczbę podów.

- Usuń ręcznie jeden pod i pokaż, że klaster sam odtwarza brakującą replikę (samonaprawianie).

- Zbuduj nową wersję obrazu (np. `ml-api:2.0`), wykonaj aktualizację kroczącą i obserwuj jej przebieg.

- Wykonaj rollback do poprzedniej wersji.

Przykład startowy:

```bash
kubectl scale deployment ml-api --replicas=4
kubectl get pods

kubectl set image deployment/ml-api ml-api=ml-api:2.0
kubectl rollout status deployment/ml-api

kubectl rollout undo deployment/ml-api
```

W sprawozdaniu opisz, co się działo z podami podczas skalowania i aktualizacji.

Na maksymalną ocenę 5 pokaż, że podczas aktualizacji kroczącej API jest cały czas dostępne (brak przerwy w działaniu).

## Zadanie 5: Konfiguracja, sondy zdrowia i limity zasobów

- Dodaj sondy `readinessProbe` oraz `livenessProbe` korzystające z endpointu zdrowia aplikacji.

- Dodaj żądania (`requests`) i limity (`limits`) zasobów CPU oraz pamięci.

- Wynieś konfigurację aplikacji do obiektu `ConfigMap` i podłącz ją do podów (np. zmienne środowiskowe).

- W sprawozdaniu opisz różnice między:

  - pojedynczym kontenerem Docker a wdrożeniem w Kubernetes;
  - podejściem deklaratywnym (manifesty YAML) a imperatywnym (`kubectl` ad-hoc);
  - sondą `readiness` a sondą `liveness`.

Przykład startowy (fragment kontenera):

```yaml
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 15
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
```

Na maksymalną ocenę 5 skonfiguruj automatyczne skalowanie poziome (Horizontal Pod Autoscaler) i pokaż, że liczba podów zmienia się pod obciążeniem. W Minikube wymaga to włączenia dodatku metrics-server:

```bash
minikube addons enable metrics-server
kubectl autoscale deployment ml-api --cpu-percent=60 --min=2 --max=6
kubectl get hpa
```

Wskazówki:  
Pamiętaj o `imagePullPolicy: IfNotPresent` dla obrazów ładowanych lokalnie, bo inaczej klaster spróbuje pobrać obraz z zewnętrznego rejestru. Jeśli pod ma status `ImagePullBackOff`, najczęściej oznacza to problem z obrazem lub jego nazwą. Stan klastra diagnozuj poleceniami `kubectl get pods`, `kubectl describe pod <nazwa>` oraz `kubectl logs <nazwa>`.

UWAGA: Rozwiązanie zadania należy przesłać w aplikacji Teams. Rozwiązaniem może być link do repozytorium GitHub/GitLab zawierającego kod aplikacji, plik `Dockerfile`, manifesty Kubernetes (`deployment.yaml`, `service.yaml` i inne) oraz plik `README.md`. Plik `README.md` będzie traktowany jako sprawozdanie: należy w nim opisać sposób uruchomienia klastra i wdrożenia, odpowiedzieć na pytania z zadań, a także dodać zrzuty ekranu z wykonania ćwiczeń (działające pody, test endpointu, skalowanie, aktualizacja).
