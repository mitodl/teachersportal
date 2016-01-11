export const PRODUCT_RESPONSE = {
  "upc": "Course_upc",
  "title": "Course title",
  "description": "Course description here",
  "external_pk": "upc",
  "product_type": "Course",
  "price_without_tax": null,
  "parent_upc": null,
  "info": {
    "overview": "overview",
    "image_url": "http://youtube.com/",
    "description": "description",
    "author_name": "author",
    "title": "title"
  },
  "children": [
    {
      "info": {
        "subchapters": [],
        "title": "other course"
      },
      "parent_upc": "Course_upc",
      "product_type": "Module",
      "title": "Chapter 1",
      "external_pk": "chap1",
      "children": [],
      "upc": "Module_chap1",
      "price_without_tax": 123.0
    },
    {
      "info": {
        "subchapters": [],
        "title": "chapter 2"
      },
      "parent_upc": "Course_upc",
      "product_type": "Module",
      "title": "Chapter 2",
      "external_pk": "chap2",
      "children": [],
      "upc": "Module_chap2",
      "price_without_tax": 345.0
    }
  ]
};

export const CART_WITH_ITEM = [{
  upc: PRODUCT_RESPONSE.children[0].upc,
  seats: 3,
  parentUpc: PRODUCT_RESPONSE.upc
}];
