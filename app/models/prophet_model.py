import pandas as pd
from prophet import Prophet

class ProphetProjection:
    name = "prophet-logistic"

    def fit_predict(
        self,
        t: list[int],
        votes: list[int],
        horizon: int,
    ) -> tuple[list[int], list[int]]:
        
        if len(t) < 2:
            # Si no hay suficientes datos, retornar vacío o el último valor constante
            if len(t) == 1:
                return [t[0] + step for step in range(1, horizon + 1)], [votes[-1]] * horizon
            return [], []

        # Prophet espera fechas, por lo que convertiremos el índice relativo 't' (ej. minutos) 
        # a una fecha ficticia a partir del epoch para entrenar el modelo.
        # Asumimos que cada paso de 't' es 1 minuto para Prophet.
        df = pd.DataFrame({
            'ds': pd.to_datetime(t, unit='m', origin='unix'),
            'y': votes
        })
        
        # Como es una votación, el conteo es acumulativo y tiene un techo lógico, 
        # pero como no nos envían el total del padrón (cap), usaremos crecimiento lineal 
        # o logística si pudiéramos inferir un cap razonable. 
        # Para ser seguros sin el cap real, usamos lineal con piso.
        m = Prophet(growth='linear', daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=False)
        m.fit(df)
        
        # Crear dataframe futuro
        last_t = t[-1]
        future_t = [last_t + step for step in range(1, horizon + 1)]
        future = pd.DataFrame({
            'ds': pd.to_datetime(future_t, unit='m', origin='unix')
        })
        
        forecast = m.predict(future)
        
        # Extraer las predicciones asegurando que sean monótonas crecientes (los votos no bajan)
        predicted = forecast['yhat'].values
        
        floor = float(votes[-1])
        monotonic: list[int] = []
        for value in predicted:
            floor = max(floor, value)
            monotonic.append(int(round(floor)))
            
        return future_t, monotonic
