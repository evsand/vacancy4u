# vacancy4u
The application analyzes your resume and searches for suitable vacancies for key skills at https://hh.ru
</br>

## Installation Instructions

### Installation

Pull down the source code from this GitHub repository:

```sh
$ git clone https://github.com/evsand/vacancy4u
```

### Docker 
Run Docker containers.
```
docker-compose build
docker-compose up
```

### HOW TO USE
- follow this link  http://localhost:5000/
- enter in the form a link to your resume from the  https://hh.ru/
- take result

![image](https://user-images.githubusercontent.com/107134912/215765401-37ca6e65-805d-4735-8003-d380e474ebc7.png)

![Screenshot from 2023-01-31 15-59-06](https://user-images.githubusercontent.com/107134912/215766698-63521d91-e3e9-429a-979b-3951f6e67cc3.png)


## TODO
- [ ] Refactor tasks.py (bad practice with call function in function with celery)
- [ ] Write tests
- [ ] MB add redis for cached search result
