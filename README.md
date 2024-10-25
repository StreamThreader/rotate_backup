# rotate_backup

== EN ==

The script is designed to automate work with backup files.

Each call performs the following steps:

1) creating weekly backups based on daily backups
2) creating monthly backups based on weekly backups
3) rotating daily backups
4) rotating weekly backups
4) rotating monthly backups

Usage instructions

The variable "rotate_dir" stores the path to the directory where daily backup copies are regularly placed.

Backup files match the pattern in the variable "name_pattern".

By default, the pattern is set to "????-??-??-v8.3-TW-ERP--??-??-".

The variables "daily_suffix", "weekly_suffix", "montly_suffix" set the endings of the file names.

As a result, examples:
* daily backup "2024-01-01-v8.3-TW-ERP--01-00-d.dt"
* weekly backup "2024-01-01-v8.3-TW-ERP--01-00-w.dt"
* monthly backup "2024-01-01-v8.3-TW-ERP--01-00-m.dt"

The variables specify how many:

* KEEP_DAYS - days to be kept
* KEEP_WEEKS -  weeks to be kept
* KEEP_MONTHS - months to be kept

A value of 0 disables file deletion.

== UK ==

Скрипт призначено для автоматизації роботи з файлами резервних копій.

Під час кожного виклику виконуються етапи:

1) створення базуючись на денних бекапів - тижневих
2) створення базуючись на тижневих бекапів - місячних
3) ротація денних бекапів
4) ротація тижневих бекапів
5) ротація місячних бекапів

Інструкція з використання

У змінній "rotate_dir" зберігатиметься шлях до директорії, куди регулярно розміщуються щоденні резевні копії.

Файли резервних копій відповідають шаблону змінної "name_pattern".

За замовчуванням шаблон встановлено "????-??-??-v8.3-TW-ERP--??-??-".

Змінними "daily_suffix", "weekly_suffix", "montly_suffix" задаються закінчення імен файлів.

В результаті приклад:
 * денний бекап "2024-01-01-v8.3-TW-ERP--01-00-d.dt"
 * тижневий бекап "2024-01-01-v8.3-TW-ERP--01-00-w.dt"
 * місячний бекап "2024-01-01-v8.3-TW-ERP--01-00-m.dt"

Змінними задається скількі зберігати:

* KEEP_DAYS - днів
* KEEP_WEEKS - неділь
* KEEP_MONTHS - місяців

Значення 0, вимикає видалення файлів.
