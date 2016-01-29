export const COURSE_RESPONSE1 = {
  "title": "Course title 1",
  "description": "Course 1 description here",
  "uuid": "course_1uuid",
  "info": {
    "overview": "overview1",
    "image_url": "http://image1/",
    "description": "description1",
    "author_name": "author1",
    "title": "title1"
  },
  "modules": [
    {
      "info": {
        "subchapters": [],
        "title": "chapter 1"
      },
      "title": "Chapter 1",
      "uuid": "chap1_uuid",
      "price_without_tax": 123.45
    },
    {
      "info": {
        "subchapters": [],
        "title": "chapter 2"
      },
      "title": "Chapter 2",
      "uuid": "chap2_uuid",
      "price_without_tax": 345.67
    }
  ]
};

export const COURSE_RESPONSE2 = {
  "title": "Course title 2",
  "description": "Course description here 2",
  "uuid": "course_uuid 2",
  "info": {
    "overview": "overview2",
    "image_url": "http://image2/",
    "description": "description 2",
    "author_name": "author 2",
    "title": "title 2"
  },
  "modules": [
    {
      "info": {
        "subchapters": [],
        "title": "chapter 1 of course 2"
      },
      "title": "Chapter 1 of course 2",
      "uuid": "chap1_course2_uuid",
      "price_without_tax": 678.90
    }
  ]
};

export const COURSE_LIST = [COURSE_RESPONSE1, COURSE_RESPONSE2];

export const CART = [
  {
    uuid: COURSE_RESPONSE1.modules[0].uuid,
    seats: 3,
    courseUuid: COURSE_RESPONSE1.uuid
  },
  {
    uuid: COURSE_RESPONSE2.modules[0].uuid,
    seats: 4,
    courseUuid: COURSE_RESPONSE2.uuid
  }
];
