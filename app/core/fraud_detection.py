import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from neo4j import GraphDatabase

class FraudDetection:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.graph_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.isolation_forest_model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
        self.scaler = StandardScaler()
        self.dbscan = DBSCAN(eps=1.5, min_samples=5)

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._preprocess_data(df)

        anomalies_iforest = self._isolation_forest(df)
        anomalies_dbscan = self._dbscan_anomaly(df)

        anomalies = pd.concat([anomalies_iforest, anomalies_dbscan]).drop_duplicates()

        return anomalies

    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df['amount'] = df['amount'].astype(float)
        df['balance'] = df['balance'].astype(float)
        transaction_type_mapping = {
            'deposit': 0,
            'withdrawal': 1,
            'buy': 2,
            'sell': 3
        }
        df['transaction_type_encoded'] = df['transaction_type'].map(transaction_type_mapping)
        df['transaction_type_encoded'] = df['transaction_type_encoded'].fillna(-1)  # Assign -1 to unknown types
        
        # Handle any remaining NaN values
        df = df.fillna(0)
        
        return df

    def _isolation_forest(self, df: pd.DataFrame) -> pd.DataFrame:
        features = df[['amount', 'transaction_type_encoded', 'balance']]
        self.isolation_forest_model.fit(features)
        df['anomaly_score'] = self.isolation_forest_model.decision_function(features)
        df['anomaly'] = self.isolation_forest_model.predict(features)
        anomalies = df[df['anomaly'] == -1]
        return anomalies

    def _dbscan_anomaly(self, df: pd.DataFrame) -> pd.DataFrame:
        features = df[['amount', 'balance']]
        scaled_features = self.scaler.fit_transform(features)
        clusters = self.dbscan.fit_predict(scaled_features)
        df['cluster'] = clusters
        anomalies = df[df['cluster'] == -1]
        return anomalies

    def graph_based_analysis(self, df: pd.DataFrame):
        with self.graph_driver.session() as session:
            session.write_transaction(self._create_graph_nodes, df)
            suspicious_users = session.read_transaction(self._detect_suspicious_users)
        return suspicious_users

    @staticmethod
    def _create_graph_nodes(tx, df: pd.DataFrame):
        for _, row in df.iterrows():
            tx.run(
                """
                MERGE (u:User {user_id: $user_id})
                MERGE (a:Account {account_id: $account_id})
                MERGE (u)-[:HAS_ACCOUNT]->(a)
                """,
                user_id=row['user_id'], account_id=row['account_id']
            )

    @staticmethod
    def _detect_suspicious_users(tx):
        result = tx.run(
            """
            MATCH (u1:User)-[:HAS_ACCOUNT]->(a:Account)<-[:HAS_ACCOUNT]-(u2:User)
            WHERE u1.user_id <> u2.user_id
            RETURN DISTINCT u1.user_id AS User1, u2.user_id AS User2, a.account_id AS SharedAccount
            """
        )
        return result.data()

    def temporal_anomaly_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df.sort_values(by=['user_id', 'created_at'], inplace=True)
        df['time_diff'] = df.groupby('user_id')['created_at'].diff().dt.total_seconds()
        rapid_transactions = df[(df['time_diff'] < 60) & (df['time_diff'] > 0)]
        return rapid_transactions
