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


export interface City {
  id: CityId;
  name: string;
}

export interface CityResponse {
    cities: City[]
}

export interface Category {
  id: CategoryId;
  name: string;
  color: HEXColor;
}

export interface CategoryResponse {
    categories: Category[]
}

export interface SubCategory {
  id: SubCategoryId;
  name: string;
  category: Category;
}

export interface SubCategoryResponse {
    subcategories: SubCategory[]
}

interface SkillImage {
  id: number;
  image: Url;
  updated_at: IsoDateTime;
}

// краткая информация о навыке
// для страницы избранного и главной страницы (используется в составе типов)
interface SkillPreview {
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

// для создания экземпляра Хочу научиться - передается в апи POST запросом
export interface WantsToLearn {
  subcategory: SubCategoryId;
}

type SkillExchangeRequestStatus =
  | "pending" // Ожидает рассмотрения
  | "accepted" // Принята
  | "rejected" // Отклонена
  | "cancelled"; // Отменена инициатором


// для Post запроса на создание заявки
export interface SkillExchangeRequest {
    recipient: number;
}

// ответ на заявку
export interface SkillExchangeRequest {
  id: SkillExchangeRequestId;
  recipient: UserId;
  recipient_full_name: string;
  status: SkillExchangeRequestStatus;
  created_at: IsoDateTime;
  responded_at: Nullable<IsoDateTime>;
}

type Gender = "male" | "female";

interface User {
  id: UserId;
  name: string;
  date_of_birth: IsoDate;
  gender: Gender;
  city: CityId;
  about: string;
  avatar: Nullable<Url>;
}

// email конфиденциальная информация, не стоит ее передавать в общем списке
export interface UserProfile extends User {
  email: string;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
}

// Для страницы избранное
export interface SkillLike {
  user: User;
  skill: SkillPreview;
  created_at: IsoDateTime;
}

export type SkillExchangeNotificationEventType =
  | "new_request" // Новая заявка на обмен
  | "accepted" // Заявка принята
  | "rejected" // Заявка отклонена
  | "cancelled"; // Заявка отменена

// информация для уведомлений.
export interface SkillExchangeNotification {
  id: number;
  request_id: SkillExchangeRequestId;  // id заявки для перехода по кнопке "перейти"
  requester_name: string;  // {requester_name} предлагает вам обмен
  event_type: SkillExchangeNotificationEventType;
  is_read: boolean;
  created_at: IsoDateTime;
}

// для главной страницы, чтобы не перегружать сервер запросами
export interface UserFull {
  id: UserId;
  name: string;
  city: City;
  gender: Gender;
  avatar: Nullable<Url>;
  skills: SkillPreview[];
  wants_to_learn: WantsToLearn[];
  age: number;
  is_liked: boolean; // лайкнул ли текущий пользователь этого юзера
  likes_count: number; // количество лайков, которые получили навыки этого пользователя
}

// пагинация для уведомлений и пользователей главной страницы
// Необходима, так как иначе пользователь будет хранить в браузере копию базы данных.
export interface PaginatedResponse<T> {
  count: number;
  next: Nullable<string>;
  previous: Nullable<string>;
  results: T[];
}

export type SkillExchangeNotificationPaginatedResponse = PaginatedResponse<SkillExchangeNotification>;
export type UserFullPaginatedResponse = PaginatedResponse<UserFull>;
