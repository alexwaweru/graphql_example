# schema.py
from ariadne import MutationType, QueryType, make_executable_schema, convert_kwargs_to_snake_case

from books.models import Book, Review, Inventory

type_defs = """
    input RatingsInput {
        ratingsValue: Int!
        ratingsOption: RatingOptions!
    }

    enum RatingOptions {
        rating__gt
        ratings__lt
        rating
    }

    type Query {
        books(title: String, author: String): [Book]
        reviews(bookId: String!, isHelpful: Boolean, rating: RatingsInput): [Review]
        items(bookId: String!): [Item]
    }

    type Mutation {
        createBook(title: String!, author: String!): Book!
        createReview(rating: Int!, isHelpful: Boolean!, bookId: String!): Review!
        createItem(remaining: Int!, price: Float!, bookId: String!): Item
    }

    type Book {
        id: ID
        title: String
        author: String
        reviews: [Review]
        items: [Item]
        createdAt: String
        updatedAt: String
    }

    type Review {
        id: ID
        book: Book
        rating: Int
        isHelpful: Boolean
        createdAt: String
        updatedAt: String
    }

    type Item {
        id: ID
        book: Book
        remaining: Int
        price: Float
        createdAt: String
        updatedAt: String
    }
"""

# mutation resolvers
mutation = MutationType()

@mutation.field("createBook")
def resolve_create_book(*_, title, author):
    new_book = Book.objects.create(title=title, author=author)
    return new_book

@mutation.field("createReview")
@convert_kwargs_to_snake_case
def resolve_create_review(*_, book_id, rating, is_helpful):
    new_review = Review.objects.create(
        book=Book.objects.get(id=book_id),
        rating=rating, 
        is_helpful=is_helpful
    )
    Book.objects.get(id=book_id).reviews.add(new_review)
    return new_review

@mutation.field("createItem")
@convert_kwargs_to_snake_case
def resolve_create_item(*_, book_id, remaining, price):
    new_item = Inventory.objects.create(
        book=Book.objects.get(id=book_id), 
        remaining=remaining, 
        price=price
    )
    Book.objects.get(id=book_id).items.add(new_item)
    return new_item

# query resolvers
query = QueryType()

@query.field("books")
def resolve_books(_, info, title=None, author=None):
    filter_args = {}
    if title:
        filter_args["title__icontains"] = title
    if author:
        filter_args["author__icontains"] = author
    
    if not filter_args:
        books = Book.objects.all()
    else:
        books = Book.objects.filter(**filter_args).all()
    
    results = []
    for book in books:
        results.append({
            "id": str(book.id),
            "title": book.title,
            "author": book.author,
            "reviews": [{
                "id": str(review.id),
                "isHelpful": review.is_helpful,
                "rating": review.rating,
                "book": {
                    "id": str(review.book.id),
                    "title": review.book.title,
                    "author": review.book.author,
                },
            } for review in book.reviews.all()],
            "items": [{
                "id": str(item.id),
                "book": {
                    "id": str(item.book.id),
                    "title": item.book.title,
                    "author": item.book.author,
                },
                "remaining": item.remaining,
                "price": item.price,
            } for item in book.items.all()],
        })

    return results


@query.field("reviews")
@convert_kwargs_to_snake_case
def resolve_reviews(_, info, book_id, is_helpful=None, rating=None):
    filter_args = {"book_id": book_id}
    if is_helpful:
        filter_args["is_helpful"] = is_helpful
    if rating:
        filter_args = {**rating ,**filter_args}

    reviews = Review.objects.filter(**filter_args).all()
    return results

@query.field("items")
@convert_kwargs_to_snake_case
def resolve_items(_, info, book_id):
    return Inventory.objects.filter(book_id=book_id).all()

schema = make_executable_schema(type_defs, mutation, query)
