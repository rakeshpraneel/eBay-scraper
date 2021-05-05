import requests as rq
from bs4 import BeautifulSoup as bs
import pandas as pds
from datetime import datetime
#https://www.ebay.com/itm/303716934606?_trkparms=5373%3A0%7C5374%3AFeatured
#class=sections-container

def check_response(URL):
    try:
        Response = rq.get(URL)
        print('The Response of the url: ', Response)
        print("\n")
        if Response.ok:
            return Response
        else:
            return 0
    except:
        print(f"Some error has occured while trying to reach {URL}")
        return 0

def Creating_file(final_list):
    x = datetime.now()
    date = x.strftime("%d") + '-' + x.strftime("%m") + '-' + str(x.year)
    #Creating filename with date appended
    FileName = 'eBay-DealOfTheDay-'+date+'.csv'
    outputdata = pds.DataFrame(final_list)
    outputdata.to_csv(FileName, index=False)
    return FileName

if __name__ == '__main__':

    #Parent url for the Site
    Url = "https://www.ebay.com/globaldeals"

    #Defining the header for the browser
    header = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}

    #Checking for the response
    response = check_response(Url)

    if response:
        #parsing the page in html
        soup = bs(response.content, 'html.parser')

        #Using dictionary inorder to index them in sheet atlast
        product_dict = {
            'Product Name': [],
            'Price': [],
            'Product Link': [],
            'Top Selling': [],
            'Special Offer': [],
            'Original Price': [],
            'Offer': [],
            'Sales Reason and Stat': []
        }

        #Checking whether any product is showcased in banner
        #Post that fetching the product details
        if soup.find('div', class_='ebayui-dne-summary-card card ebayui-dne-item-featured-card--topDeals'):
            banner_product = soup.find('div', class_='ebayui-dne-summary-card card ebayui-dne-item-featured-card--topDeals')
            banner_product_name = banner_product.find('span', itemprop='name').get_text()
            banner_product_price = banner_product.find('span', itemprop='price').get_text()
            print(banner_product_name)
            print(banner_product_price)
            #Here we r checking whether url is provided
            if banner_product.find('a', href=True):
                #we r getting the href value which is nothing but the url of that product
                banner_product_url = banner_product.find('a', href=True)['href']
                print(banner_product_url)
            else:
                banner_product_url = '-'
            #Here we r checking whether there is on demand icon
            if banner_product.find('div', class_='dne-itemcard-hotness-icon icon-deals-hotness'):
                #If the icon is present then the product is selling fast
                print("Product is selling fast")
                banner_product_sellfast = 'Yes'
                if banner_product_url:
                    indivi_response = check_response(banner_product_url)
                    if indivi_response:
                        indivi_soup = bs(indivi_response.content, 'html.parser')
                        if indivi_soup.find('div', id='why2buy'):
                            banner_product_sold = ((indivi_soup.find('div', id='why2buy').get_text()).strip()).split('\n')
                            print(banner_product_sold)
                    else:
                        banner_product_sold = '-'
                        print(f"Error reaching {banner_product_url}")
            else:
                banner_product_sellfast = 'No'
                banner_product_sold = '-'
            #Here we r checking whether PST price is there
            if banner_product.find('span', class_='itemtile-price-strikethrough'):
                #If it is so then there is some spl offer is going on for this product
                #Then we r grabbing the actual price and offer provided for this product
                org_price = banner_product.find('span', class_='itemtile-price-strikethrough').get_text()
                print(f"This product is in special offer, orginal price is {org_price}")
                offer_percent = banner_product.find('span', class_='itemtile-price-bold').get_text()
                print(f"Offer applied: {offer_percent}")
                spl_offer = 'Yes'
            else:
                org_price = '-'
                offer_percent = '-'
                spl_offer = 'No'
            product_dict['Product Name'].append(str(banner_product_name).upper())
            product_dict['Product Link'].append(banner_product_url)
            product_dict['Price'].append(banner_product_price)
            product_dict['Original Price'].append(org_price)
            product_dict['Special Offer'].append(spl_offer)
            product_dict['Top Selling'].append(banner_product_sellfast)
            product_dict['Offer'].append(offer_percent)
            product_dict['Sales Reason and Stat'].append(banner_product_sold)
        #Final_List.append(product_dict)

        # grepping the values which comes under class row
        # In ebay the products are stacked in row and column wise
        product_list = soup.find_all('div', class_='row')
        print(product_list)
        print("\n")

        #Looping through the columns to find each and every product details
        for rows in product_list:
            for products in rows:
                #We are again doing the same process which we did for product in banner
                product_name = products.find('span', itemprop='name').get_text()
                product_price = products.find('span', itemprop='price').get_text()
                print(product_name)
                print(product_price)
                if products.find('a', href=True):
                    product_url = products.find('a', href=True)['href']
                    print(product_url)
                else:
                    product_url = '-'
                if products.find('div', class_='dne-itemcard-hotness-icon icon-deals-hotness'):
                    product_sellfast = 'Yes'
                    print("Product is selling fast")

                    #As it is fast seller, we r scraping the reason of selling
                    #And stats of the sale
                    if product_url:
                        indivi_response = check_response(product_url)
                        if indivi_response:
                            indivi_soup = bs(indivi_response.content, 'html.parser')
                            if indivi_soup.find('div', id='why2buy'):
                                product_sold = ((indivi_soup.find('div', id='why2buy').get_text()).strip()).split('\n')
                                print(product_sold)
                        else:
                            print(f"Error reaching {product_url}")
                            product_sold = '-'
                else:
                    product_sellfast = 'No'
                    product_sold = '-'
                if products.find('span', class_='itemtile-price-strikethrough'):
                    org_price = products.find('span', class_='itemtile-price-strikethrough').get_text()
                    print(f"This product is in special offer, orginal price is {org_price}")
                    offer_percent = products.find('span', class_='itemtile-price-bold').get_text()
                    print(f"Offer applied: {offer_percent}")
                    spl_offer = 'Yes'
                else:
                    org_price = '-'
                    offer_percent = '-'
                    spl_offer = 'No'
                product_dict['Product Name'].append(product_name)
                product_dict['Product Link'].append(product_url)
                product_dict['Price'].append(product_price)
                product_dict['Original Price'].append(org_price)
                product_dict['Special Offer'].append(spl_offer)
                product_dict['Top Selling'].append(product_sellfast)
                product_dict['Offer'].append(offer_percent)
                product_dict['Sales Reason and Stat'].append(product_sold)
        print(product_dict)
        filecreated = Creating_file(product_dict)
        print(f"File {filecreated} Created!!!")
    else:
        print(f"Error reaching {Url}....Please check your network connection!!!")