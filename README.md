# ProdukcyjnePayUAPI

Stworzone w ramach nauki korzystania z REST API.

[Dokumentacja techniczna PayU](http://developers.payu.com/pl/restapi.html#creating_new_order_api)

## Klucze

W pliku secrets.json znajdują się przykładowe ([publiczne](http://developers.payu.com/pl/overview.html#sandbox)) wartości `posId`/`client_id` i `client_secret`.

Program korzysta z danych zapisanych jako JSON (zamiast bazy danych SQL) ze względu na zakładane nastawienie na integrację z API.

W przyszłości powstanie wersja z użyciem Flaska i bazy danych. Zadziała tam też `notifyUrl`.

## TO-DO:

* rejestracja użytkowników
* przekierowania od PayU z paramterami - wywołanie sprawdzania, czy użytkownik zapłacił
* interfejs webowy
* SQL zamiast JSONa
