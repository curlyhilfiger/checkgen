# Тестовое задание для разработчика на python

У сети ресторанов доставки "ФорФар" есть множество точек, на которых готовятся заказы для клиентов.
Каждый клиент хочет вместе с заказом получить чек, содержащий детальную информацию о заказе.
Сотрудники кухни также хотят чек, чтобы в процессе готовки и упаковки заказа не забыть положить всё что нужно.
Наша задача помочь и тем и другим, написав сервис для генерации чеков.

### Схема работы сервиса

1. Сервис получает информацию о новом заказа, создаёт в БД чеки для всех принтеров точки указанной в заказе и ставит асинхронные задачи на генерацию PDF-файлов для этих чеков. Если у точки нет ни одного принтера - возвращает ошибку. Если чеки для данного заказа уже были созданы - возвращает ошибку.
2. Асинхронный воркер с помощью wkhtmltopdf генерируют PDF-файл из HTML-шаблон. Имя файла должно иметь следущий вид <ID заказа>\_<тип чека>.pdf (123456_client.pdf).
   Файлы должны хранится в папке media/pdf в корне проекта.
3. Приложение опрашивает сервис на наличие новых чеков. Опрос происходит по следующему пути: сначала запрашивается список чеков которые уже сгенерированы для конкретного принтера, после скачивается PDF-файл для каждого чека и отправляется на печать.
