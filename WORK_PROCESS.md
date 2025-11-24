# Взаимодействие с Гитхабом

## 1) Получить актуальные данные:
```bash
git checkout main
git pull origin main
```

## 2) Создать новую ветку:
```bash
git checkout -b <название_ветки>
```

## 3) Коммитим изменения:
```bash
git add "все файлы которые поменялись"
git commit -m "описание изменений"
git push origin <название_ветки>
```

## 4) Делаем MR (Merge Request)
- Заходим на GitHub
- Создаем Pull Request
- Выбираем TL

## 5) Код ревью
- Ждем проверки коллеги
- Исправляем замечания если есть

## 6) Решаем конфликты (если отстали от main):
```bash
git checkout <название_ветки>
git rebase main
# Решаем конфликты для КАЖДОГО коммита!
git add "все файлы которые поменялись"
git rebase --continue
git push origin <название_ветки> --force-with-lease
```
