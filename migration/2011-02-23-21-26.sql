
alter table jobsite_main_searchevent add column active boolean not null default true;
alter table jobsite_main_userevent add column active boolean not null default true;
