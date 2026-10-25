"""Venue fee formulas (taker). Per memory/notes: Kalshi 0.07*p*(1-p) per contract, rounded up
to the cent per order; Polymarket rate*p*(1-p) per share (feeSchedule.exponent == 1), rate 0 on
political markets."""
import math

def kalshi_fee(price, qty, mult=0.07):
    if qty <= 0: return 0.0
    return math.ceil(round(mult * qty * price * (1 - price) * 100, 6)) / 100

def kalshi_unit(price, mult=0.07):
    return mult * price * (1 - price)

def pm_fee(price, qty, rate):
    return rate * price * (1 - price) * qty

def pm_unit(price, rate):
    return rate * price * (1 - price)
