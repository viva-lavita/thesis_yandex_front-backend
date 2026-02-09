export type Nullable<T> = T | null;
export type IsoDate = string;
export type IsoDateTime = string;
export type HEXColor = string;
export type Url = string;

export type CityId = number;
export type CategoryId = number;
export type SubCategoryId = number;
export type SkillId = number;
export type SkillExchangeRequestId = number;
export type UserId = number;

// пагинация
// export type SubCategoryPaginatedResponse = PaginatedResponse<SubCategory>;
// Необходима, так как иначе пользователь будет хранить в браузере копию базы данных.
export interface PaginatedResponse<T> {
  count: number;
  next: Nullable<string>;
  previous: Nullable<string>;
  results: T[];
}

export interface City {
  id: CityId;
  name: string;
}

export interface Category {
  id: CategoryId;
  name: string;
  color: HEXColor;
}

export interface SubCategory {
  id: SubCategoryId;
  name: string;
  category: Category;
}

interface SkillImage {
  id: number;
  image: Url;
  updated_at: IsoDateTime;
}

// краткая информация о навыке
// для страницы избранного и главной страницы (используется в составе типов)
export interface SkillPreview {
  id: SkillId;
  name: string;
  subcategory: SubCategory;
  images: SkillImage[];
}
// полная информация о навыке
// для страницы навыка
export interface Skill extends SkillPreview {
  description: Nullable<string>;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
}

// для создания экземпляра Хочу научиться - передается в апи
export interface WantsToLearn {
    "subcategory": SubCategoryId;
}

type SkillExchangeRequestStatus =
  | 'pending' // Ожидает рассмотрения
  | 'accepted' // Принята
  | 'rejected' // Отклонена
  | 'cancelled'; // Отменена инициатором

// заявка на обмен навыками
export interface SkillExchangeRequest {
    "id": SkillExchangeRequestId;
    "recipient": UserId;
    "recipient_full_name": string;
    "status": SkillExchangeRequestStatus;
    "created_at": IsoDateTime;
    "responded_at": Nullable<IsoDateTime>;
}

type Gender = 'male' | 'female';


export interface User {
    "id": UserId;
    "name": string;
    "date_of_birth": IsoDate;
    "gender": Gender;
    "city": CityId;
    "about": string;
    "avatar": Nullable<Url>;
}

// Для страницы избранное
export interface SkillLike {
    "user": User;
    "skill": Skill;
    "created_at": IsoDateTime;
}
