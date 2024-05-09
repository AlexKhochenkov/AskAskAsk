from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from faker import Faker
import random

from django.db import connection

from app.models import Question, Answer, Upvote, Tag, Profile

class Command(BaseCommand):

    def add_arguments(self, parser):
        return parser.add_argument('ratio', type=int)
    
    def handle(self, *args: Any, **options: Any):
        ratio=options['ratio']
        fake=Faker()
        users=[]
        profiles=[]
        questions=[]
        tags=[]
        answers=[]
        upvotes=[]
        self.stdout.write(self.style.SUCCESS(f'Creating {ratio} users'))
        for i in range(ratio):
            new_user=User(username=fake.unique.user_name(), email=fake.unique.email(), password=fake.password())
            users.append(new_user)
            new_profile=Profile(user=new_user, birth_date=fake.date())
            profiles.append(new_profile) 
            new_tag=Tag(name=fake.text(max_nb_chars=8)+f' {i}')
            tags.append(new_tag)
        Tag.objects.bulk_create(tags)
        User.objects.bulk_create(users)
        self.stdout.write(self.style.SUCCESS(f'Creating {ratio*10} questions'))
        ratio_q=ratio*10
        for i in range(ratio_q):
            new_question=Question(title=fake.sentence(nb_words=4),
                                  content=fake.text(max_nb_chars=140),
                                  user=users[random.randint(0, ratio-1)],
                                  date_written=fake.date(),
                                  )
            questions.append(new_question)
        Question.objects.bulk_create(questions)
        ratio_a=ratio*100
        for i in range(ratio_a):
            new_answer=Answer(content=fake.text(max_nb_chars=140),
                              date_written=fake.date(),
                              user=users[random.randint(0, ratio-1)],
                              question=questions[random.randint(0, ratio_q-1)])
            answers.append(new_answer)
        Answer.objects.bulk_create(answers)
        self.stdout.write(self.style.SUCCESS(f'Creating {ratio*200} users'))
        ratio_u=ratio*200
        for i in range(ratio_u):
            my_vote=fake.boolean()
            if my_vote:
                my_vote=1
            else:
                my_vote=-1
            my_qa_bool=fake.boolean()
            if my_qa_bool:
                my_qa=questions[(i)%ratio_q]
            else:
                my_qa=answers[(i)%ratio_q]
            new_upvote=Upvote(vote=my_vote,
                              user=users[random.randint(0, ratio-1)],
                              content_type=ContentType.objects.get_for_model(my_qa),
                              object_id=random.randint(1, ratio_q-1))
            upvotes.append(new_upvote)
        Profile.objects.bulk_create(profiles) 
        self.stdout.write(self.style.SUCCESS(f'Assigning tags...'))  
        questions_=Question.objects.all()
        for question in questions_:
            question.tags.set(random.sample(list(Tag.objects.all()), 2))
        Upvote.objects.bulk_create(upvotes)


    


            
