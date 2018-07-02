# curly-octo-spork
CLI for adding financial reports ad dokuwiki

na ten moment pipenv jako skopana forma interakcji, potem setup.py

```shell
pipenv install
pipenv run python finansonator.py --help
pipenv run python finansonator.py -i mbank.csv -v
```


Ok, co ja chcę

    - [ ] brać pliki i robić z nich zagregowane csv
        * cli otrzymuje listę plików które ma przetworzyć
        * stwierdza czy są poprawne headery które wpisane w scheme
        * odrzucić niepoprawne
        * concatenacja ich bez powtórzeń
        * agregacja do tabeli
        * export do dowolnego pliku
    - [ ] zagregowany raport wysłać
        * na odopowiednią stronę wiki
        * dodawać odpowiednio sformatowany wpis
        alkdfla;dk;f;alsd