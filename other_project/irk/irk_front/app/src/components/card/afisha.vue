<template>
  <a href="{{ url }}" class="card">
    <div class="card__info">
        <div class="card__info__top">
            <span class="card__label">
                {{ label }}
            </span>
            <span class="card__time">
                <time v-if="date"
                \ datetime="{{ date }}">{{ date }}</time>
                <p v-else > уточняется </p>
                </span>
        </div>
        <div class="card__info__bottom">
            <h4 class="card__title">
                {{ title }}
            </h4>
            <div class="card__desc">
                {{ caption }}
            </div>
        </div>
    </div>
    <div class="card__bg">
        <img src="{{ thumb }}" />
    </div>
</a>

  </template>

<script>
export default {
  name: 'CardAfisha',
  props: [
    'material',
    'title',
    'caption',
    'url',
    'image_url',
  ],
};
</script>
