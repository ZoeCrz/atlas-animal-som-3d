"""SOM de Kohonen con una retícula cúbica real y 20 pesos por neurona.

El PHP original presenta la interfaz; sus bucles de aprendizaje están en JS.
Aquí NumPy reemplaza esos bucles sin delegar el algoritmo a una librería SOM.
"""
from dataclasses import dataclass
from typing import Callable, Optional
import numpy as np


@dataclass(frozen=True)
class SOMConfig:
    grid_size: int = 5
    epochs: int = 80
    learning_rate: float = 0.5
    sigma: float = 2.0
    seed: int = 42
    distance: str = "manhattan"

    def __post_init__(self):
        if type(self.grid_size) is not int or not 2 <= self.grid_size <= 10:
            raise ValueError("El lado del grid debe ser entero entre 2 y 10.")
        if type(self.epochs) is not int or not 1 <= self.epochs <= 300:
            raise ValueError("Las épocas deben ser un entero entre 1 y 300.")
        if not np.isfinite(self.learning_rate) or not 0 < self.learning_rate <= 1:
            raise ValueError("La tasa de aprendizaje debe estar entre 0 y 1, excluyendo 0.")
        if not np.isfinite(self.sigma) or not 0.5 <= self.sigma <= 10:
            raise ValueError("El radio inicial debe estar entre 0.5 y 10.")
        if type(self.seed) is not int or not 0 <= self.seed <= 2**32 - 1:
            raise ValueError("La semilla debe ser un entero válido de 32 bits.")
        if self.distance not in ("manhattan", "euclidean"):
            raise ValueError("Distancia no compatible.")


class SOM3D:
    def __init__(self, config: SOMConfig = SOMConfig()):
        self.config = config
        # El original usa FC*FC neuronas. La extensión usa FC*FC*FC.
        self.coordinates = np.indices((config.grid_size,) * 3).reshape(3, -1).T
        self.weights = None
        self.history = []

    @staticmethod
    def _validate(data):
        array = np.asarray(data, dtype=float)
        if array.ndim != 2 or min(array.shape) == 0:
            raise ValueError("Los datos deben ser una matriz no vacía.")
        if not np.isfinite(array).all() or (array < 0).any() or (array > 1).any():
            raise ValueError("Todos los valores deben ser finitos y estar entre 0 y 1.")
        return array

    def _distances(self, sample):
        # El JS suma diferencias absolutas: es Manhattan, aunque su comentario dice euclidiana.
        difference = self.weights - sample
        if self.config.distance == "manhattan":
            return np.abs(difference).sum(axis=1)
        return np.sqrt(np.square(difference).sum(axis=1))

    def _check_fitted(self):
        if self.weights is None:
            raise ValueError("Primero entrena el mapa.")

    def train(self, data, progress: Optional[Callable[[int, int], None]] = None):
        data = self._validate(data)
        # Una semilla reproduce tanto los pesos aleatorios como el orden de muestras.
        rng = np.random.default_rng(self.config.seed)
        self.weights = rng.random((len(self.coordinates), data.shape[1]))
        self.history = [{"Época": 0, "Error de cuantización": self.quantization_error(data)}]
        for epoch in range(self.config.epochs):
            fraction = epoch / max(self.config.epochs - 1, 1)
            alpha = self.config.learning_rate * 0.1**fraction
            sigma = self.config.sigma * (0.5 / self.config.sigma)**fraction
            for sample in data[rng.permutation(len(data))]:
                # argmin acepta coincidencias exactas: no se descartan D=0 ni D=1 como en JS.
                winner = int(np.argmin(self._distances(sample)))
                squared_grid_distance = np.square(self.coordinates - self.coordinates[winner]).sum(axis=1)
                neighborhood = np.exp(-squared_grid_distance / (2 * sigma**2))
                # Regla de Kohonen: W += alpha * vecindad * (entrada - W).
                self.weights += alpha * neighborhood[:, None] * (sample - self.weights)
            if (epoch + 1) % 5 == 0 or epoch + 1 == self.config.epochs:
                self.history.append({"Época": epoch + 1,
                                     "Error de cuantización": self.quantization_error(data)})
            if progress is not None:
                progress(epoch + 1, self.config.epochs)
        return self

    def map(self, data):
        self._check_fitted()
        data = self._validate(data)
        if data.shape[1] != self.weights.shape[1]:
            raise ValueError("La cantidad de características no coincide con el modelo.")
        indices = np.asarray([np.argmin(self._distances(sample)) for sample in data], dtype=int)
        return self.coordinates[indices].copy()

    def quantization_error(self, data):
        self._check_fitted()
        data = self._validate(data)
        if data.shape[1] != self.weights.shape[1]:
            raise ValueError("La cantidad de características no coincide con el modelo.")
        # Ambas métricas se normalizan a [0,1] para facilitar su lectura.
        divisor = data.shape[1] if self.config.distance == "manhattan" else np.sqrt(data.shape[1])
        return float(np.mean([self._distances(sample).min() / divisor for sample in data]))

    def topographic_error(self, data):
        self._check_fitted()
        data = self._validate(data)
        if data.shape[1] != self.weights.shape[1]:
            raise ValueError("La cantidad de características no coincide con el modelo.")
        failures = []
        for sample in data:
            first, second = np.argsort(self._distances(sample), kind="stable")[:2]
            # Vecindad de 6 caras: dos nodos son adyacentes si difieren una unidad en un eje.
            failures.append(np.abs(self.coordinates[first] - self.coordinates[second]).sum() != 1)
        return float(np.mean(failures))

    def nearest(self, sample, data, count=5):
        data = self._validate(data)
        sample = self._validate([sample])[0]
        if sample.shape[0] != data.shape[1]:
            raise ValueError("Las características no coinciden.")
        differences = np.abs(data - sample)
        distances = differences.mean(axis=1) if self.config.distance == "manhattan" else np.sqrt(np.square(differences).mean(axis=1))
        indices = np.argsort(distances, kind="stable")[:count]
        return indices, distances[indices]
