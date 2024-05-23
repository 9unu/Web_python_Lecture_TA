from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import random
import warnings
from selenium import webdriver
options = webdriver.ChromeOptions()
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

def Coupang_Crawling(product_name=None, page_num=30, Logging ="넹"):
    # 1~3초 랜덤 딜레이 시간 설정
    random_sec=random.uniform(1,3)
    
    # 최종으로 만들 데이터 프레임
    Coupang_df=pd.DataFrame(columns=["브랜드", "제품명", "검색 순위", "배송비", "쿠팡 판매가", "쿠팡 판매가 단위별 가격", "와우 할인가", "와우 할인가 단위별 가격", "상품평 수"])

    keyword= product_name   # 검색할 제품
    list_size=72    #상품을 한페이지에 몇개씩 띄울건지 선택 (48, 60, 72)
    link_list=[]    # 상품 링크를 추가할 리스트
    
    """
    페이지 이동 (for문)
    쿠팡의 검색창에 keyword를 입력했을 때 나오는 화면에 나오는 제품 링크를 크롤링
    """

    for page_num in range(1, page_num+1):
        print(f"<<<<<<<<{page_num}페이지>>>>>>>>>")
        url=f"https://www.coupang.com/np/search?component=&q={keyword}&page={page_num}&listSize={list_size}"    # 쿠팡 제품 url 구조

        # 쿠팡의 요청 헤더에 맞춰서 헤더 수정 (꼭 필요함!)
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}
        # 위의 url에 request를 보냄 -> 응답(상태코드, header, text, json 등의 웹페이지 정보)을 받음
        response=requests.get(url, headers=headers) 
        # 받은 응답에서 text를 지정(웹페이지 HTML 내용)
        html=response.text
        # 문자열로된 HTML을 HTML 요소를 검색, 조작할 수 있는 BeautifulSoup 객체로 변환 
        soup = BeautifulSoup(html, "html.parser")
        
        # 화면에 띄워진 제품들을 크롤링 (select함수 사용)
        items=soup.select("[class=search-product]") # 광고 딱지 안붙은 제품
        items_ad=soup.select(".search-product__ad-badge") # 광고 딱지 붙은 제품
        items_all=soup.select(".search-product") # 정규 추천 + 한정시간 특가 + 같이 보면 좋은 상품, 이상품을 검색한 다른 사람들이 함께 본 상품 전부
        
        # 크롬 드라이버로 검색 화면을 띄움 (쿠팡에 직접 검색하는 것과 코드를 통해 검색한 결과가 다를 수 있음! 오해 금지!)
        # driver = webdriver.Chrome(options=options)
        # driver.get(url)

        # 모든 제품 링크를 link_list 변수에 순서대로 저장
        for item in items:
            link=f"https://www.coupang.com{item.a['href']}" # 상품 링크
            link_list.append(link)
        
        time.sleep(random_sec)  # ip막히는 것 대비
    print("제품 링크를 모두 수집했습니다.")

    """
    제품 페이지 이동 (for문)
    위에서 구한 제품 링크를 순회하면서 제품 페이지 탐색 -> 제품 정보 크롤링
    1. 상품 순위 (화면의 좌측 상단일 수록 순위가 높다고 가정)
    2. 브랜드명
    3. 제품 이름
    4. 상품평 수
    5. 배송비 (없으면 None)
    6. 쿠팡 판매가
    7. 쿠팡 판매가 (g당 가격)
    8. 와우 회원 할인가
    9. 와우 회원 할인가 (g당 가격)
    출력시에는 디버깅 및 출력 확인을 위해 url도 포함시켰습니다!
    """
    print("제품 정보 크롤링 시작!")
    for rank, url in enumerate(link_list):
        rank+=1
        time.sleep(random_sec)
        # 웹페이지 내용 받아오기
        response=requests.get(url, headers=headers) 
        # html파일(웹페이지)전체를 텍스트로 변환
        html=response.text
        soup = BeautifulSoup(html, "html.parser")
        # 브랜드명
        brand=soup.select_one(".prod-brand-name").text.strip() #빈 공간 제거
        
        # 제품 이름
        title=soup.select_one(".prod-buy-header__title").text.strip()
        
        # 상품평 수
        rating_cnt=soup.select_one(".prod-buy-header__info")
        if rating_cnt:
            rating_cnt=rating_cnt.select_one(".count").text.strip()
        
        # 배송비
        delivery_fee = soup.select_one(".delivery-fee-info")
        if delivery_fee:
            delivery_fee=delivery_fee.text[4:].strip()
        # 쿠팡 판매가
        origin_price_box = soup.select_one(".prod-sale-price")
        # 즉시 할인가 (만약 쿠팡 판매가 하나만 나와있는 경우 즉시 할인가로 쿠팡 판매가가 나옴)
        saled_price_box = soup.select_one(".prod-coupon-price")
        
        # 즉시 할인가가 있는 경우
        if saled_price_box:
            saled_price=saled_price_box.select_one(".total-price").text.strip()
            saled_per_price=saled_price_box.select_one(".unit-price")
            if saled_per_price:
                saled_per_price=saled_per_price.text.strip()
            else:
                saled_per_price=""
            
        # 쿠팡 판매가가 있는 경우
        if origin_price_box:
            origin_price=origin_price_box.select_one(".total-price").text.strip()
            origin_per_price=origin_price_box.select_one(".unit-price")
            # g 당 가격을 안알려주는 경우가 있음
            if origin_per_price:
                origin_per_price=origin_per_price.text.strip()
            else:
                origin_per_price=""
        # 쿠팡 판매가가 없는 경우에는 즉시 할인가가 쿠팡 판매가로 나옴
        else:
            origin_price=saled_price
            origin_per_price=saled_per_price
            saled_price="없음"
            saled_per_price=""
        
        if Logging =="넹":
            print(f"브랜드: {brand}, 제품명:{title}")
            print("url:",url)
            print("검색 순위:", rank)
            print("배송비:", delivery_fee)
            print("쿠팡 판매가:", origin_price, origin_per_price)
            print("와우 할인가:", saled_price, saled_per_price)
            print("상품평 수:", rating_cnt[:-4])
            print("-"*50)
        new_row=[brand, title, rank, delivery_fee, origin_price, origin_per_price, saled_price, saled_per_price, rating_cnt[:-4]]
        Coupang_df.loc[len(Coupang_df)]=new_row
        
    return Coupang_df

if __name__ == "__main__":
    df = Coupang_Crawling(product_name=input("제품명:"), page_num=int(input("검색할 페이지수:")), Logging=(input("프린트?:")))
    df.to_csv("Coupang_df.csv", index=False)