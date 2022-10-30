# web-review-processing
 An application to scrape TripAdvisor pages, retrieve reviews, and apply NLP algorithms on the reviews.

---
 - In the review-scrape-soup.py file, i use BeautifulSoup4 to scrape reviews from any TripAdvisor page. As an example, i scraped reviews from:
    - [Vero Bistro Moderne](https://www.tripadvisor.com/Restaurant_Review-g154913-d1119735-Reviews-Vero_Bistro_Moderne-Calgary_Alberta.html "VERO BISTRO MODERNE, Calgary - Tripadvisor").
    - [Caesar's Steak House & Lounge](https://www.tripadvisor.com/Restaurant_Review-g154913-d683068-Reviews-Caesar_s_Steak_House_Lounge-Calgary_Alberta.html "CAESAR'S STEAK HOUSE & LOUNGE, Calgary - Tripadvisor").

> The code is completely commented in portuguese to help with understanding.

 - In the review-nlp.py file, i plan to use NLTK to apply some NLP algorithms to the CSV files generated with review-scrape-soup.py.

> The code is still a Work In Progress.
<img src="https://connect-asia.org/wp-content/uploads/WORK-IN-PROGRESS-ICON-01-1024x928.png" alt="drawing" width="200"/>
