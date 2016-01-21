export const COURSE_RESPONSE = {
  "title": "Course title",
  "description": "Course description here",
  "uuid": "course_uuid",
  "info": {
    "overview": "overview",
    "image_url": "http://youtube.com/",
    "description": "description",
    "author_name": "author",
    "title": "title"
  },
  "modules": [
    {
      "info": {
        "subchapters": [],
        "title": "other course"
      },
      "title": "Chapter 1",
      "uuid": "chap1_uuid",
      "price_without_tax": 123.0
    },
    {
      "info": {
        "subchapters": [],
        "title": "chapter 2"
      },
      "title": "Chapter 2",
      "uuid": "chap2_uuid",
      "price_without_tax": 345.0
    }
  ]
};

export const CART_WITH_ITEM = [{
  uuid: COURSE_RESPONSE.modules[0].uuid,
  seats: 3,
  courseUuid: COURSE_RESPONSE.uuid
}];
