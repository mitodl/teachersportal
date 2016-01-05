export const PRODUCT_RESPONSE = {
  "upc": "Course_7560bd21-7b1d-4c2f-8103-acc93b6c40b1",
  "title": "Course 7560bd21-7b1d-4c2f-8103-acc93b6c40b1",
  "description": "Course description here",
  "external_pk": "7560bd21-7b1d-4c2f-8103-acc93b6c40b1",
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
      "parent_upc": "Course_7560bd21-7b1d-4c2f-8103-acc93b6c40b1",
      "product_type": "Module",
      "title": "Module ed99737e-d5bf-4b95-a467-bf4ecf31f7b0",
      "external_pk": "ed99737e-d5bf-4b95-a467-bf4ecf31f7b0",
      "children": [],
      "upc": "Module_ed99737e-d5bf-4b95-a467-bf4ecf31f7b0",
      "price_without_tax": 33.0
    }
  ]
};

export const CART_WITH_ITEM = [{
  upc: PRODUCT_RESPONSE.children[0].upc,
  seats: 3,
  parentUpc: PRODUCT_RESPONSE.upc
}];
