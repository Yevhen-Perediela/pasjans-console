## PASJANS w terminalu


### Tryby

- 1 – łatwy (dobierana 1 karta)
- 3 – trudny (dobierane 3 karty)

###  Sterowanie

| Komenda       | Co robi                                                      |
|---------------|--------------------------------------------------------------|
| `d`           | Dobiera kartę ze stosu                                       |
| `u`           | Cofnij ostatni ruch                                          |
| `m X Y`       | Przenieś kolumnę z `X` do `Y` (np. `m 3 7`)                  |
| `f X`         | Przenieś ostatnią kartę z kolumny `X` do stosu końcowego     |
| `w Y`         | Przenieś kartę ze stosu (waste) do kolumny `Y`               |
| `wf`          | Przenieś kartę ze stosu (waste) do stosu końcowego           |
| `h`           | Podpowiedz możliwy ruch (podświetli zieloną ramką kartę)     |
| `q`           | Wyjście z gry                                                |

---

### Dodatkowo

- Gra zapamiętuje 3 ostatnich stanów (można cofnąć `u`).
- Komenda `h` pokazuje jedną możliwą akcję (np. przeniesienie Asa).


---

### Aby uruchomić wpisz:
./start.sh - (Linux) \n
start.bat - (Windows)

- Zalecam zmniejszyć zoom ekranu (Ctrl + -) dla wygody korzystania z gry