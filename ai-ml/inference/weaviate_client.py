from weaviate import connect_to_local, init

class WeaviateClientSingleton:
    """Singleton to manage a single instance of the Weaviate client."""
    _client_instance = None

    @classmethod
    def get_client(cls):
        if cls._client_instance is None:
            cls._client_instance = connect_to_local(
                additional_config=init.Configure(
                    timeout=init.Timeout(init=10),  # Customize timeout
                )
            )
            print("Weaviate client initialized.")
        return cls._client_instance

    @classmethod
    def close_client(cls):
        if cls._client_instance:
            cls._client_instance.close()
            cls._client_instance = None
            print("Weaviate client connection closed.")
