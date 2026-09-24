# API quick reference

### List reviews
GET `/reviews?page=1&limit=20`

Optional query parameters:
- `product`
- `rating`
- `sentiment`
- `q`

### One review
GET `/reviews/syn-0000001`

### Products
GET `/products?page=1&limit=24&q=tablet`

### Stats
GET `/stats`

### Interactive documentation
GET `/docs`
