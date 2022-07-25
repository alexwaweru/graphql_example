# schema.py
from ariadne import MutationType, QueryType, make_executable_schema

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
def resolve_create_review(*_, book_id, rating, is_helpful):
    new_review = Review.objects.create(
        book=Books.objects.get(id=book_id),
        rating=rating, 
        is_helpful=is_helpful
    )
    return new_review

@mutation.field("createItem")
def resolve_create_item(*_, book_id, remaining, price):
    new_item = Inventory.objects.create(
        book=Books.objects.get(id=book_id), 
        remaining=remaining, 
        price=price
    )
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

    return Book.objects.filter(**filter_args)

@query.field("reviews")
def resolve_reviews(_, info, book_id, is_helpful=None, rating=None):
    filter_args = {"book_id": book_id}
    if is_helpful:
        filter_args["is_helpful"] = is_helpful
    if rating:
        filter_args = {**rating ,**filter_args}

    return Review.objects.filter(**filter_args)

@query.field("items")
def resolve_items(_, info, book_id):
    return Inventory.objects.filter(book_id=book_id)

schema = make_executable_schema(type_defs, mutation, query)