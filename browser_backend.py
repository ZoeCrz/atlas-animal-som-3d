"""Motor de la versión de un solo HTML. Corre sin cambios en CPython y Pyodide.

JavaScript dibuja y recoge entradas; Python valida, entrena y asigna las BMU.
Las operaciones se aplican únicamente después de completar su validación.
"""
import json
from dataclasses import asdict
import numpy as np
from animal_validation import validate_collection, export_custom, import_custom
from features import FEATURES
from som import SOM3D, SOMConfig


class BrowserSession:
    def __init__(self, initial):
        self.base = validate_collection(initial['base'])
        self.extra = []
        self.include_extra = False
        self.model = SOM3D(SOMConfig(**initial['config']))
        weights = np.asarray(initial['weights'], dtype=float)
        if weights.shape != (self.model.config.grid_size**3, len(FEATURES)):
            raise ValueError('Pesos iniciales incompatibles.')
        if not np.isfinite(weights).all() or (weights < 0).any() or (weights > 1).any():
            raise ValueError('Pesos iniciales inválidos.')
        self.model.weights = weights
        self.model.history = initial['history']

    def snapshot(self):
        animals = self.base + self.extra
        data = np.asarray([a['features'] for a in animals], dtype=float)
        differences = np.abs(data[:, None, :] - data[None, :, :])
        distances = (differences.mean(axis=2) if self.model.config.distance == 'manhattan'
                     else np.sqrt(np.square(differences).mean(axis=2)))
        neighbors = []
        for i, row in enumerate(distances):
            order = [int(j) for j in np.argsort(row, kind='stable') if j != i][:3]
            neighbors.append([{'index': j, 'distance': float(row[j])} for j in order])
        return {'animals': animals, 'positions': self.model.map(data).tolist(),
                'neighbors': neighbors, 'config': asdict(self.model.config),
                'include_extra': self.include_extra, 'extra': self.extra,
                'history': self.model.history,
                'error': self.model.quantization_error(data)}

    def dispatch(self, request_json, progress=None):
        request = json.loads(request_json)
        command, payload = request['command'], request.get('payload', {})
        if command == 'train':
            config = SOMConfig(**payload['config'])
            include = payload.get('include_extra', False)
            if type(include) is not bool:
                raise ValueError('La opción de entrenamiento debe ser booleana.')
            animals = self.base + (self.extra if include else [])
            candidate = SOM3D(config).train([a['features'] for a in animals], progress)
            self.model, self.include_extra = candidate, include
        elif command == 'add':
            additions = validate_collection([payload['animal']], self.base + self.extra)
            extra = self.extra + additions
            if self.include_extra:
                candidate = SOM3D(self.model.config).train(
                    [a['features'] for a in self.base + extra], progress)
                self.model = candidate
            self.extra = extra
        elif command == 'import':
            extra = import_custom(payload['json'].encode('utf-8'), self.base)
            if self.include_extra:
                candidate = SOM3D(self.model.config).train(
                    [a['features'] for a in self.base + extra], progress)
                self.model = candidate
            self.extra = extra
        elif command == 'reset':
            candidate = SOM3D(SOMConfig()).train([a['features'] for a in self.base], progress)
            self.extra, self.include_extra, self.model = [], False, candidate
        elif command == 'export':
            return export_custom(self.extra)
        elif command != 'snapshot':
            raise ValueError('Operación no compatible.')
        return json.dumps(self.snapshot(), ensure_ascii=False)
