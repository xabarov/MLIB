import type { MissionDefinition } from './missionTypes'

export const kernelHuntMission: MissionDefinition = {
  id: 'kernel-hunt',
  route: '/algebra/linear-maps/kernel',
  title: 'Охота за ядром',
  domain: 'linear-algebra',
  mechanic: 'geometry-lab',
  lessonPath: 'SHAD/algebra/8_Linear_maps/lesson.md',
  difficulty: 1,
  levels: [
    {
      id: 'nonzero-zero',
      title: 'Не ноль, но в ноль',
      objective: 'Подбери ненулевой вектор x так, чтобы Ax стало нулевым.',
      hint: 'Смотри на две ошибки: x + y и x - z. Их нужно занулить одновременно.',
      successText: 'Есть ненулевой вектор ядра: матрица отправляет его в ноль.',
    },
    {
      id: 'solution-line',
      title: 'Прямая решений',
      objective: 'Найди второй вектор ядра, отличный от первого.',
      hint: 'Если умножить найденное направление на другое число, ты останешься в ядре.',
      successText: 'Решения тянутся вдоль одной прямой через начало.',
    },
    {
      id: 'kernel-basis',
      title: 'Базис ядра',
      objective: 'Выставь вектор в направлении (-1, 1, -1) или противоположном.',
      hint: 'Координаты должны иметь одинаковые модули, а первая и третья - один знак.',
      successText: 'Одного направления достаточно: ядро одномерно.',
    },
    {
      id: 'rank-nullity',
      title: 'Ранг плюс дефект',
      objective: 'Собери финальное равенство: 3 = rank A + dim ker A.',
      hint: 'Матрица имеет две независимые строки, а ядро дает одно свободное направление.',
      successText: 'Ранг 2 и дефект 1 складываются в размерность исходного пространства.',
    },
  ],
}

export const determinantForgeMission: MissionDefinition = {
  id: 'determinant-forge',
  route: '/algebra/determinants/forge',
  title: 'Кузница определителя',
  domain: 'linear-algebra',
  mechanic: 'geometry-lab',
  lessonPath: 'SHAD/algebra/5_Det/lesson.md',
  difficulty: 1,
  levels: [
    {
      id: 'area-two',
      title: 'Сделай площадь 2',
      objective: 'Поставь два вектора так, чтобы площадь параллелограмма стала равна 2.',
      hint: 'Площадь параллелограмма равна |det A|.',
      successText: 'Площадь поймана: модуль определителя равен 2.',
    },
    {
      id: 'flip-orientation',
      title: 'Поменяй ориентацию',
      objective: 'Сделай det A отрицательным, сохранив заметную площадь.',
      hint: 'Поменяй порядок обхода пары векторов: знак определителя сменится.',
      successText: 'Ориентация изменилась: знак определителя стал отрицательным.',
    },
    {
      id: 'break-invertibility',
      title: 'Сломай обратимость',
      objective: 'Схлопни параллелограмм так, чтобы det A стал равен 0.',
      hint: 'Два вектора должны лечь на одну прямую.',
      successText: 'Матрица вырождена: площадь исчезла.',
    },
    {
      id: 'repair-matrix',
      title: 'Почини матрицу',
      objective: 'Верни det A отличным от нуля одним движением.',
      hint: 'Чуть отведи один вектор от общей прямой.',
      successText: 'Матрица снова обратима: площадь вернулась.',
    },
  ],
}
