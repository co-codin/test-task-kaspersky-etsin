sudo nano /etc/proxychains4.conf

# добавить эти прокси в proxychains4 и включить tor server
```socks5 127.0.0.1 9050 ```
```http 192.168.1.1 8080```


```КАК ИСПОЛЬЗОВАТЬ - ```
```python3 devbrute.py -s twitter -u testuser -w passwords.txt -d 1```