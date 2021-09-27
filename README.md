# database-mongodb-tp

TP M2 MongoDB Database

- MIQUTE Gautier
- WILLEMS Louis

## Getting started

Clone and install dependencies:

```bash
git clone https://github.com/Xisabla/database-mongodb-tp
cd database-mongodb-tp
pip3 install -r requirements.txt
```

## 1 & 2 

- get self-services bicycle stations from APIs
- worker that refreshes and store live data

```bash
./worker.py --verbose
```

see: [`worker.py`](worker.py)

## 3 - User program

- give available stations next to given `lat` and `lon` with last data

```bash
./find_station.py <lat> <lon> --target <city>
```

see: [`find_station.py`](find_station.py)

## 4 - Business program

- find station with name
- update station
- delete station

see: [`operations.py`](operations.py)