import { createRouter, createWebHistory } from 'vue-router'
import TitleView from '../views/TitleView.vue'
import CharacterSelectView from '../views/CharacterSelectView.vue'
import GameView from '../views/GameView.vue'
import ResultView from '../views/ResultView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'title',
      component: TitleView,
    },
    {
      path: '/select',
      name: 'select',
      component: CharacterSelectView,
    },
    {
      path: '/game',
      name: 'game',
      component: GameView,
    },
    {
      path: '/result',
      name: 'result',
      component: ResultView,
    },
  ],
})

export default router
