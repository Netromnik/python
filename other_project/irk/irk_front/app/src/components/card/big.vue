<template>
  <div class="bigcard">
    <div class="bigcard__inner">
        <div class="bigcard__header">
            <span class="bigcard__label">
                {{ label }}
            </span>
            <span class="bigcard__info">
                45 комментариев, около 8 минут на чтение
            </span>
        </div>
        <div class="bigcard__article">
            <h3 class="bigcard__title">
                {{ title }}
            </h3>
            <p class="bigcard__desc">
                {{ caption }}
            </p>
        </div>
        <div class="bigcard__bottom">
            <a href="{{ url }}" class="bigcard__button">
                Читать на сайте
            </a>
        </div>
    </div>
    <div class="bigcard__bg">
        <img src="{{ image }}" />
    </div>
</div>
  </template>

<script>
export default {
  name: 'Big',
  props: [
    'label',
    'title',
    'caption',
    'url',
    'image_url',
  ],
};
</script>
