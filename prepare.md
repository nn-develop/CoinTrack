--- add_new_coin
    - HTTP Method: POST
    - Endpoint: /coins/
    - Description: Adds a new cryptocurrency to the database.
    - Parameters: id, symbol, name
    - Validation: Verify the symbol using Coingecko API before adding.

--- get_coin
    - HTTP Method: GET
    - Endpoint: /coins/{id}
    - Description: Retrieves a cryptocurrency by its ID.

--- update_coin
    - HTTP Method: PUT
    - Endpoint: /coins/{id}
    - Description: Updates the details of an existing cryptocurrency.

--- delete_coin
    - HTTP Method: DELETE
    - Endpoint: /coins/{id}
    - Description: Deletes a cryptocurrency from the database.

--- get_coins_list
    - HTTP Method: GET
    - Endpoint: /coins/
    - Description: Retrieves a list of all cryptocurrencies.

--- verify_coin_from_api
    - Description: Separate the logic for querying the Coingecko API to verify the existence of a cryptocurrency symbol.

--- update_coin_from_api
    - Description: Separate the logic for updating cryptocurrency data using the Coingecko API.

--- run_periodical_update
    - Description: Implement a periodic task to update cryptocurrency data, separated from the Coingecko API logic.

--- Caching with Redis
    - Description: Store data from the Coingecko API in Redis with an expiration timestamp.
    - Strategy: Before querying the Coingecko API, check if the data is available and up-to-date in Redis.
    - Functions:
        - `get_coin_from_cache(symbol: str) -> Optional[Coin]`: Retrieve coin data from Redis if available.
        - `store_coin_in_cache(coin: Coin) -> None`: Store coin data in Redis with an expiration timestamp.
        - `is_coin_data_fresh(symbol: str) -> bool`: Check if the coin data in Redis is still fresh.

--- ukládání dat o coinech do PostgreSQL (pomocí SQLAlchemy asynchronně)
    - Description: Store cryptocurrency data in a PostgreSQL database using SQLAlchemy asynchronously.
    - Implementation:
        - Define SQLAlchemy models for the coin data.
        - Use async SQLAlchemy sessions for database operations.
        - Ensure proper exception handling and connection management.
    - Functions:
        - `create_coin(coin: Coin) -> None`: Add a new coin to the PostgreSQL database.
        - `get_coin_by_id(coin_id: int) -> Optional[Coin]`: Retrieve a coin by its ID from the PostgreSQL database.
        - `update_coin(coin_id: int, updated_data: Dict[str, Any]) -> None`: Update an existing coin's data in the PostgreSQL database.
        - `delete_coin(coin_id: int) -> None`: Delete a coin from the PostgreSQL database.
        - `list_all_coins() -> List[Coin]`: Retrieve a list of all coins from the PostgreSQL database.

Basic code rules:
- Python 3.13
- async api, use asyncio
- DRY and SOLID principles
- must use type hints everywhere (without typing library)


Domácí úkol
Vaším úkolem je vytvořit jednoduché API rozhraní pro vkládání a zobrazení kryptoměn. Jak
provedete, je převážně už ve Vašich rukou. Fantazii se meze nekladou a důležitých je jen
několik málo bodů.

Co chceme vidět ?
● Chceme vidět co umíte a co Vás baví.
● Async API postavené nad FastAPI knihovnou s CRUD metodami pro operace se
záznamem kryptoměny v databázi.
● Pokud máte chuť a volný čas, součástí může být i frontend, ale to je skutečně jen
třešnička na dortu.
● Aby úkol byl zábavnější, při vkládání kryptoměny ověřte existenci symbolu pomocí
volání API na Coingecko, můžete uložit získané informace a použít je jako metadata
záznamu.
● https://www.coingecko.com/en/api/documentation
● Pokud aplikace dokáže uložené informace pomoci Coingecko API i sama
aktualizovat, určitě se nebudeme zlobit :)
Technologie
● Python, fastapi, postgresql, redis, sqlalchemy, gino, asyncio …
● Tyto technologie už používáme, pokud je použijete také budeme rádi.
● Nemusíte použít vše a necháme se překvapit i nějakou novou knihovnou co ještě
neznáme.
Odevzdání
● Jen jak jste se svým projektem spokojen, pošlete nám odkaz na git repozitář.
● Odevzdání není na čas, ale čím dříve uvidíme výsledek, tím dříve se můžeme
posunout dále.
● Následovat bude prostor pro "obhajobu" řešení a reakce na review, nemusí být vše
na 100% hotovo, je možné popsat i další vývoj slovně.
Závěrem
● Pokud máte dotaz, nebojte se zeptat v připraveném kanálu.
Těšíme se na výsledek! Hodně štěstí!