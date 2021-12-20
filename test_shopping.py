from conftest import amazon_price, bestbuy_price


def test_shopping():


    assert amazon_price < bestbuy_price
