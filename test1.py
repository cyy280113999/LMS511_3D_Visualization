from TelegramProcess import *
dataB = b'\x02sRA LMDscandata 0 1 119883A 0 0 2796 2801 F87F5C00 F87FA401 0 0 3F 0 0 1388 168 0 1 DIST1 40000000 00000000 0 1388 F1 363 364 35B 35A 35A 342 33F 33E 341 344 341 353 35A 35F 35D 37A 38E 38E 39A 3A4 3A6 3AE 3B8 3BF 3C3 3C2 3C5 3CE 3D6 3DA 3E0 3E3 3E0 3E5 3E9 3E6 3EB 3EF 3F4 410 4E5 4FB 501 505 508 50B 511 518 51E 4E0 4D5 4E2 51B 4E4 4D0 4F9 4DE 4BC 4B2 4B4 49D 48E 484 481 484 487 491 495 49E 4A9 4AD 4B1 4BB 4C2 4CD 4D3 4DB 4E9 4ED 4F7 4FD 508 50E 51D 525 531 53C 544 551 55C 567 570 57D 58D 596 5A5 5B1 5C0 5D0 5E0 5EE 5FD 60E 622 62F 63F 64D 664 676 689 6A0 6B6 6C9 6DD 6F8 70C 725 73B 756 76E 789 7A8 7C4 7E0 804 823 844 865 88D 8AF 8D2 8FE 926 956 982 9B0 9E3 A17 A50 A84 ABD B02 B41 B85 BD3 C1D C6F CC2 D1A D76 DE3 E5D EDC F5E FF2 1095 1146 11FD 12D3 13C8 14BB 15CB 16EC 185A 1941 194F 1948 1945 194C 1958 1957 1962 1966 0 0 7B96 7B98 7BA9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\x03'
data = data_process(dataB)[:10]
for da in data:
    print(da)