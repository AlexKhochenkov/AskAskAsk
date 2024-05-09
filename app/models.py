from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.db import models

# Create your models here.


class ProfileManager(models.Manager):
    def best_users(self):
        profiles = self.annotate(
            # raiting=Coalesce(Sum('user__questions__upvotes__vote')+
                            # Sum('user__answers__upvotes__vote'), 0)
            raiting=Coalesce(Count('user__answers'),0)
        )
        return profiles.order_by('-raiting')[:5]

class UpvoteManager(models.Manager):
    use_for_related_fields=True

    def toggle_like(self, content_object, user, vote):
        if self.filter(user=user, content_type=ContentType.objects.get_for_model(content_object), object_id=content_object.id).exists():
            self.filter(user=user, content_type=ContentType.objects.get_for_model(content_object), object_id=content_object.id).delete()
        else:
            self.create(user=user, content_type=ContentType.objects.get_for_model(content_object), object_id=content_object.id, vote=vote)

    def rating(self):
        rating=self.get_queryset().filter(vote__gt=0).count() - self.get_queryset().filter(vote__lt=0).count()
        return rating
    
    def is_liked(self, content_object, user):
        return self.filter(user=user, content_type=ContentType.objects.get_for_model(content_object), object_id=content_object.id).exists()

class QuestionManager(models.Manager):
    def calculate_rating(self):
        questions = Question.objects.annotate(
            raiting=Coalesce(Sum('upvotes__vote'), 0)
        )
        return questions

    def recent(self):
        questions = self.calculate_rating()
        return questions.order_by('-date_written', '-raiting')
    
    def get_likes(self, id):
        question = Question.objects.get(id=id)
        upvotes=Upvote.objects.all().filter(content_type=ContentType.objects.get_for_model(question), object_id=question.id)
        sum=0
        for upvote in upvotes:
            sum+=upvote.vote
        return sum

    def hot(self):
        questions = self.calculate_rating()
        return questions.order_by('-raiting')

    def tag(self, tag):
        questions = self.calculate_rating()
        questions = questions.filter(tags__name=tag)
        return questions.order_by('-raiting')
    
class AnswerManager(models.Manager):
    def calculate_raiting(self):
        answers = Answer.objects.annotate(
            raiting=Coalesce(Sum('upvotes__vote'), 0)
        )
        return answers
    
    def get_likes(self, id):
        answer = Answer.objects.get(id=id)
        upvotes=Upvote.objects.all().filter(content_type=ContentType.objects.get_for_model(answer), object_id=answer.id)
        sum=0
        for upvote in upvotes:
            sum+=upvote.vote
        return sum

    def hot(self , question_id):
        answers = self.calculate_raiting()
        answers = answers.filter(question__id=question_id)
        return answers.order_by('-raiting')

class TagManager(models.Manager):
    def calculate_questions(self):
        tags = self.annotate(
            question_num=Coalesce(Count('question'), 0)
        )
        return tags

    def hot(self):
        tags = self.calculate_questions()
        return tags.order_by('-question_num')[:10]

class Upvote(models.Model):
    VOTE_CHOICES = (
        (1, 'Upvote'),
        (-1, 'Downvote')
    )
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)
    user = models.ForeignKey(User, max_length=256, on_delete=models.PROTECT)
    content_type=models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id=models.PositiveIntegerField()
    content_object=GenericForeignKey('content_type', 'object_id')

    objects=UpvoteManager()
    
class Question(models.Model):
    title = models.CharField(max_length=64)
    content = models.CharField(max_length=256)
    user = models.ForeignKey(User, max_length=256, related_name='questions', on_delete=models.PROTECT)
    date_written=models.DateField() 
    tags = models.ManyToManyField('Tag', related_name='questions', related_query_name='question')
    upvotes = GenericRelation(Upvote)

    objects=QuestionManager()

    def __str__(self):
        return self.title
    

class Answer(models.Model):
    content = models.CharField(max_length=256)
    date_written=models.DateField() 
    user = models.ForeignKey(User, max_length=256, related_name='answers', on_delete=models.PROTECT)
    question = models.ForeignKey('Question', max_length=256, related_name='answers', on_delete=models.PROTECT)
    upvotes = GenericRelation(Upvote)
    correct = models.BooleanField(default=False)

    objects=AnswerManager()

    def __str__(self):
        return self.question.title

class Tag(models.Model):
    name = models.CharField(max_length=16)

    objects=TagManager()

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    avatar=models.ImageField(null=True,blank=True,default='Question.jpeg', upload_to="avatar/%Y/%M/%D")
    date_registrated=models.DateField(null=True, blank=True) 
    birth_date=models.DateField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='profile')

    objects=ProfileManager()

    def __str__(self):
        return self.user.username
    

