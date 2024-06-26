**1) Оценить потенциал проекта. Насколько важно решить задачу?** 

Проблема: пользователям нужен разнообразный опыт на площадке, который позволяет им а) найти релевантные товары в рамках известных текущих интересов и б) выйти за их рамки, получив новый опыт от взаимодействия с новыми для себя категориями объявлений. 

*Здесь должен быть абзац, который иллюстрирует тезис на основе данных.* Однако применительно к рекомендациям, на мой взгляд, главная метрика - долгосрочный ретеншн, который без АБ и долгих экспериментов с продуктом не измерить.

Экспертно-интуитивная оценка: ~каждый 10 пользователь совершает заказ с рекомендаций на главной *(уточнить по тейлам из аналитики?)*. Следовательно, имея качественные рекомендации мы можем улучшать пользовательский опыт напрямую, показывая релевантные объявления (мб оценить эффект на выручку блока от изменения конверсии в клик и заказ), и косвенно, формируя пользовательские привычки на платформе.

**2) Есть ли простое решение? Насколько оно решит задачу? Сложно ли поддерживать такое решение?**

Есть простое решение в виде популярного по срезам пола, возраста и гео фичей, которое можно дополнительно улучшить домешиванием свежих объявлений и рандома с набором эвристик. 

Такое решение значительно легче поддерживать с технической точки зрения: на порядок меньше ресурсов за счет ограниченного числа выдач и отсутствия необходимости обучать и инференсить тяжелые модели.

Однако, это решение плохо отвечает требованиям персонализации, ведь поведение каждого пользователя можно назвать уникальным, и такое решение лишь на очень большом приближении описывает его, оставляя совсем небольшой набор инструментов для влияния на баланс между exploitation и exploration.

**3) Реалистичность решения проблемы с помощью машинного обучения.**

В большинстве пейперов по рекомендательным системам сравнивают оффлайн метрики как ndcg, map и другие. На датасетах с небольшим кол-вом объектов, с которыми пользователь может провзаимодействовать, действительно можно получить высокие метрики точности и полноты. Но ожидать сопоставимых значений на масштабе Авито с на порядок большим кол-вом объявлений было бы странно.

Наше решение скорее всего будет сильно ограничено с точки зрения оффлайн метрик даже в случае использования sota моделей и подходов. Но рекомендации на главной - важный продукт, который помогает пользователю решить свою задачу на платформе. Сделать его по настоящему персонализированным и полезным юзеру без использования машинного обучения видится еще более сложной и нетривиальной задачей. 

#### Другие важные вопросы, которые стоит иметь в виду.

- Технические требования к задаче.

В формулировке проекта заложена нагрузка 1 запрос в секунду, что в условиях работающей рекомендательной системы непозволительная роскошь. Хоть у нас нет доступа к сопоставимым с продовыми ресурсам, нам все же стоит попытаться обеспечить лучший rps. Основные сложности: быстрый доступ к пользовательским фичам, быстрый поиск ближайших, оптимальное время работы бизнес слоя, разумное время на постоянное переобучение модели.  

- Выделение ресурсов команды на интеграцию.

Для того, чтобы наш сервис использовался в проде, необходимо содействие со стороны команд приложений, которые смогут показывать пользователю нужную выдачу. У них могут быть дополнительные требования к качеству и скорости ответов сервиса.
